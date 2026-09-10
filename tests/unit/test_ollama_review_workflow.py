"""Execute the workflow's real JavaScript with mocked GitHub and Ollama APIs."""

import json
import subprocess
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).parents[2] / ".github/workflows/codex-review.yml"


def run_review(**case):
    workflow = yaml.safe_load(WORKFLOW.read_text())
    step = workflow["jobs"]["review"]["steps"][0]
    harness = r"""
const fs = require('node:fs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const c = input.case;
const calls = {requests: [], comments: [], failures: [], outputs: {}};
process.env.OLLAMA_API_KEY = c.missing_key ? '' : 'test-only-key';
process.env.OLLAMA_ENDPOINT = c.endpoint || 'https://ollama.com/api/chat';
process.env.OLLAMA_MODEL = c.model || 'glm-5.3-flash';
const pull = {number: 272, state: 'open', head: {sha:'abc'}, base: {sha:'def'},
  changed_files: 1, title: 'Synthetic PR', body: 'Untrusted text'};
const context = {repo: {owner:'example', repo:'repo'}, payload:{pull_request:pull}};
let reads = 0;
const github = {rest:{pulls:{
  get: async () => {reads++; return {data: {...pull,
    head:{sha: c.stale && reads >= (c.stale_read || 2) ? 'changed' : 'abc'}}};},
  listFiles: 'listFiles'
}, issues:{createComment: async data => {
  if (c.comment_error) throw new Error('private comment error test-only-key');
  calls.comments.push(data);
}}},
paginate: async () => c.files || [{filename:'api/example.py', additions:1, deletions:1,
  patch:'@@ -1 +1 @@\n-old\n+new'}]};
const core = {setFailed: msg => calls.failures.push(msg),
  setOutput:(key,value)=>calls.outputs[key]=value};
const fetch = async (url, options) => {
  calls.requests.push({url, ...options, body:JSON.parse(options.body)});
  if (c.network_error) throw new Error('private backend error test-only-key');
  return {ok: c.http_ok !== false, status: c.http_ok === false ? 401 : 200,
    json: async () => c.response || {done:true, done_reason:'stop', message:{
      role:'assistant', content: c.content || JSON.stringify({
        verdict:'SAFE TO MERGE', summary:'No blocking findings.', findings:[]})}}};
};
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
(async()=>{
  try {await new AsyncFunction('github','context','core','fetch',input.script)(github,context,core,fetch);}
  catch(e) {calls.failures.push(String(e));}
  process.stdout.write(JSON.stringify(calls));
})();
"""
    result = subprocess.run(
        ["node", "-e", harness],
        input=json.dumps({"script": step["with"]["script"], "case": case}),
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_cloud_review_uses_requested_model_and_posts_head_bound_feedback():
    result = run_review()
    assert result["failures"] == []
    request = result["requests"][0]
    assert request["url"] == "https://ollama.com/api/chat"
    assert request["headers"]["Authorization"] == "Bearer test-only-key"
    assert request["body"]["model"] == "glm-5.3-flash"
    assert request["body"]["stream"] is False
    assert "format" not in request["body"]  # Ollama Cloud does not support structured outputs.
    assert request["redirect"] == "error"
    assert "abc" in result["comments"][0]["body"]
    assert "test-only-key" not in result["comments"][0]["body"]


@pytest.mark.parametrize(
    "case",
    [
        {"missing_key": True},
        {"endpoint": "http://ollama.com/api/chat"},
        {"endpoint": "https://user:password@ollama.com/api/chat"},
        {"endpoint": "https://ollama.com/api/chat?key=bad"},
        {"http_ok": False},
        {"network_error": True},
        {"comment_error": True},
        {"content": "Verdict: SAFE TO MERGE"},
        {"content": '{"verdict":"SAFE TO MERGE"}'},
        {"content": '{"verdict":"UNKNOWN","summary":"x","findings":[]}'},
        {"response": {"done": False, "message": {"content": "{}"}}},
        {"response": {"done": True, "done_reason": "length", "message": {"content": "{}"}}},
        {"files": []},
        {"files": [{"filename": "asset.bin", "additions": 0, "deletions": 0}]},
        {"files": [{"filename": "x.py", "additions": 2, "deletions": 0, "patch": "+one"}]},
        {
            "files": [
                {"filename": "x.py", "additions": 1, "deletions": 0, "patch": "+" + "x" * 400001}
            ]
        },
        {"stale": True},
    ],
)
def test_review_fails_closed_without_approval(case):
    result = run_review(**case)
    assert result["failures"]
    assert result["comments"] == []
    assert "test-only-key" not in json.dumps(result["failures"])


@pytest.mark.parametrize("verdict", ["NEEDS FIX", "NEEDS DISCUSSION"])
def test_blocking_verdict_posts_feedback_but_fails(verdict):
    result = run_review(
        content=json.dumps({"verdict": verdict, "summary": "Review needed", "findings": []})
    )
    assert result["failures"]
    assert len(result["comments"]) == 1


def test_safe_verdict_cannot_override_blocking_findings():
    result = run_review(
        content=json.dumps(
            {
                "verdict": "SAFE TO MERGE",
                "summary": "Review",
                "findings": [
                    {"priority": "P1", "path": "api/example.py", "line": 1, "detail": "Tenant leak"}
                ],
            }
        )
    )
    assert result["failures"]


def test_workflow_never_executes_pr_code_or_grants_merge_permissions():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    job = workflow["jobs"]["review"]
    assert job["name"] == "codex-pr-review-gate"
    assert job["permissions"]["contents"] == "read"
    env = job["steps"][0]["env"]
    assert env["OLLAMA_API_KEY"] == "${{ secrets.OLLAMA_API_KEY }}"
    assert env["OLLAMA_MODEL"] == "${{ vars.OLLAMA_MODEL || 'glm-5.3-flash' }}"
    assert env["OLLAMA_ENDPOINT"] == "${{ vars.OLLAMA_ENDPOINT || 'https://ollama.com/api/chat' }}"
    assert not any("checkout" in step.get("uses", "") or "run" in step for step in job["steps"])
    source = WORKFLOW.read_text()
    assert "pull_request_target" not in source
    assert "OPENAI_API_KEY" not in source
    assert "OLLAMA_API_KEY" in source
    assert "continue-on-error" not in source


def test_update_during_publication_cannot_pass_review():
    result = run_review(stale=True, stale_read=3)
    assert result["failures"]
    assert len(result["comments"]) == 1


def test_nonblocking_findings_and_explicit_configuration_are_preserved():
    report = {
        "verdict": "SAFE TO MERGE",
        "summary": "Nonblocking feedback",
        "findings": [
            {"priority": "P2", "path": "api/example.py", "line": 2, "detail": "Improve naming"}
        ],
    }
    result = run_review(
        content=json.dumps(report), model="test-model", endpoint="https://approved.example/api/chat"
    )
    assert result["failures"] == []
    assert result["requests"][0]["url"] == "https://approved.example/api/chat"
    assert result["requests"][0]["body"]["model"] == "test-model"


def test_feedback_is_inert_and_redacts_the_key():
    result = run_review(
        content=json.dumps(
            {"verdict": "SAFE TO MERGE", "summary": "test-only-key @everyone ```", "findings": []}
        )
    )
    assert result["failures"] == []
    body = result["comments"][0]["body"]
    assert "test-only-key" not in body
    assert "@everyone" not in body
    assert body.count("```") == 2
