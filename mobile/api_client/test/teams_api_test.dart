import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for TeamsApi
void main() {
  final instance = SignupflowApi().getTeamsApi();

  group(TeamsApi, () {
    // Add Team Members
    //
    // Add members to team (admin only).
    //
    //Future addTeamMembers(String teamId, TeamMemberAdd teamMemberAdd) async
    test('test addTeamMembers', () async {
      // TODO
    });

    // Create Team
    //
    // Create a new team (admin only).
    //
    //Future<TeamResponse> createTeam(TeamCreate teamCreate) async
    test('test createTeam', () async {
      // TODO
    });

    // Delete Team
    //
    // Delete team (admin only).
    //
    //Future deleteTeam(String teamId) async
    test('test deleteTeam', () async {
      // TODO
    });

    // Get Team
    //
    // Get team by ID. Users can only view teams from their own organization.
    //
    //Future<TeamResponse> getTeam(String teamId) async
    test('test getTeam', () async {
      // TODO
    });

    // List Teams
    //
    // List teams. Users can only see teams from their own organization.
    //
    //Future<ListResponseTeamResponse> listTeams({ String orgId, String q, int limit, int offset }) async
    test('test listTeams', () async {
      // TODO
    });

    // Remove Team Members
    //
    // Remove members from team (admin only).
    //
    //Future removeTeamMembers(String teamId, TeamMemberRemove teamMemberRemove) async
    test('test removeTeamMembers', () async {
      // TODO
    });

    // Update Team
    //
    // Update team (admin only).
    //
    //Future<TeamResponse> updateTeam(String teamId, TeamUpdate teamUpdate) async
    test('test updateTeam', () async {
      // TODO
    });

  });
}
