# i18n Quick Start Guide

## 🚀 What's Working Now

### Supported Languages
- ✅ **English (en)** - 100% complete
- ✅ **Spanish (es)** - 100% complete
- 🚧 **Portuguese (pt)** - Partial (30%)
- 🚧 **French (fr)** - Ready for translation
- 🚧 **Chinese Simplified (zh-CN)** - Ready for translation
- 🚧 **Chinese Traditional (zh-TW)** - Ready for translation

### How to Use

**1. User switches language:**
- Go to Settings → Language selector
- Choose language from dropdown
- Page reloads with new language

**2. Developer adds translations:**
```javascript
// In your code
const buttonText = i18n.t('common.buttons.save'); // Auto-translates based on user's language
```

**3. Add new translation keys:**
```json
// In locales/en/common.json
{
  "new_feature": {
    "title": "My New Feature"
  }
}

// In locales/es/common.json
{
  "new_feature": {
    "title": "Mi Nueva Función"
  }
}
```

## 📋 Adding a New Language

**Step 1:** Create directory
```bash
mkdir -p /home/ubuntu/rostio/locales/de  # German example
```

**Step 2:** Copy English files and translate
```bash
cp locales/en/*.json locales/de/
# Then translate each file
```

**Step 3:** Add to supported languages
In `frontend/js/i18n.js`:
```javascript
this.supportedLocales = ['en', 'es', 'pt', 'fr', 'zh-CN', 'zh-TW', 'de'];
```

In `frontend/index.html`:
```html
<option value="de">Deutsch</option>
```

## 🌍 Translation Status

| File | EN | ES | PT | FR | ZH-CN | ZH-TW |
|------|----|----|----|----|-------|-------|
| common.json | ✅ | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| auth.json | ✅ | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| events.json | ✅ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| schedule.json | ✅ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| settings.json | ✅ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| admin.json | ✅ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| messages.json | ✅ | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |

## 💡 Next Steps

1. **Complete remaining translations** - Copy Spanish files and translate to PT, FR, ZH-CN, ZH-TW
2. **Update frontend code** - Replace hardcoded strings with `i18n.t()` calls
3. **Test language switching** - Verify all languages work correctly
4. **Add backend i18n** - Translate API error messages

## 🔧 For Translators

**Translation files:** `/home/ubuntu/rostio/locales/{language}/`

**Guidelines:**
- Keep `{parameter}` placeholders unchanged
- Maintain church terminology consistency
- Consider regional variations
- Test with longest translations

**Example:**
```json
{
  "events": {
    "assignment": {
      "assigned": "Assigned {name} to event as {role}"
    }
  }
}
```
Becomes in Spanish:
```json
{
  "events": {
    "assignment": {
      "assigned": "Asignado {name} al evento como {role}"
    }
  }
}
```

## ✅ Testing

```bash
# 1. Start server
poetry run uvicorn api.main:app --reload

# 2. Open browser to http://localhost:8000

# 3. Go to Settings → Language → Select "Español"

# 4. Verify UI switches to Spanish
```

