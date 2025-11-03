# Internationalization (i18n) Analysis for Rostio

## 📊 Current State Analysis

### Scope of Translatable Content

**Frontend (HTML/JS):**
- 16 frontend files (HTML + JavaScript)
- ~66 UI text instances in HTML
- ~161 user messages (toasts, alerts, confirmations)
- Form labels, buttons, navigation, error messages

**Backend (Python/FastAPI):**
- API error messages and responses
- Email templates (invitation system)
- PDF report generation
- Calendar event descriptions

### Key Challenges Identified

1. **Hardcoded text everywhere** - No centralized string management
2. **Dynamic content** - JavaScript-generated UI elements
3. **Server-side messages** - API responses, emails, PDFs
4. **Date/time formatting** - Already has timezone support, needs locale formatting
5. **Right-to-left (RTL) languages** - Arabic, Hebrew support needs CSS considerations

---

## 🏗️ Best Practices & Architecture

### 1. **Translation File Format: JSON**

**Why JSON?**
- ✅ Native JavaScript support (no parsing needed)
- ✅ Easy to read/edit for translators
- ✅ Nested structure for organization
- ✅ Compatible with translation tools

**Structure:**
```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "confirm": "Confirm"
  },
  "nav": {
    "schedule": "Schedule",
    "events": "Events",
    "availability": "Availability"
  },
  "messages": {
    "save_success": "Settings saved successfully!",
    "delete_confirm": "Are you sure you want to delete {item}?"
  }
}
```

### 2. **Frontend i18n Strategy**

#### Option A: **i18next** (Recommended)
- Most popular i18n framework
- Vanilla JS compatible
- Features: interpolation, pluralization, context
- Fallback language support

```javascript
// Setup
import i18next from 'i18next';

i18next.init({
  lng: 'en', // default language
  fallbackLng: 'en',
  resources: {
    en: { translation: enTranslations },
    es: { translation: esTranslations }
  }
});

// Usage
i18next.t('messages.save_success'); // "Settings saved successfully!"
i18next.t('messages.delete_confirm', { item: 'event' }); // "Are you sure you want to delete event?"
```

#### Option B: **Custom Lightweight Solution**
For minimal bundle size:

```javascript
// i18n.js
class I18n {
  constructor(locale = 'en') {
    this.locale = locale;
    this.translations = {};
  }

  async loadTranslations(locale) {
    const response = await fetch(`/locales/${locale}.json`);
    this.translations = await response.json();
  }

  t(key, params = {}) {
    const keys = key.split('.');
    let value = this.translations;

    for (const k of keys) {
      value = value[k];
      if (!value) return key; // fallback to key
    }

    // Replace {param} with values
    return Object.entries(params).reduce(
      (str, [key, val]) => str.replace(`{${key}}`, val),
      value
    );
  }

  setLocale(locale) {
    this.locale = locale;
    this.loadTranslations(locale);
  }
}

// Global instance
const i18n = new I18n();
```

### 3. **Backend i18n Strategy (FastAPI)**

#### Use **Babel + Python gettext**

```python
# api/utils/i18n.py
from babel import Locale
from babel.support import Translations
import gettext

class I18nManager:
    def __init__(self):
        self.translations = {}

    def load_translations(self, locale: str):
        if locale not in self.translations:
            self.translations[locale] = gettext.translation(
                'messages',
                localedir='locales',
                languages=[locale],
                fallback=True
            )
        return self.translations[locale]

    def translate(self, message: str, locale: str = 'en', **kwargs):
        t = self.load_translations(locale)
        translated = t.gettext(message)
        return translated.format(**kwargs) if kwargs else translated

i18n = I18nManager()

# Usage in API
@router.post("/events/{event_id}/assignments")
def assign_person(event_id: str, locale: str = "en"):
    # ...
    return {
        "message": i18n.translate(
            "Assigned {name} to event as {role}",
            locale,
            name=person.name,
            role=request.role
        )
    }
```

### 4. **Language Detection Strategy**

**Priority Order:**
1. **User preference** (stored in database)
2. **Browser settings** (`Accept-Language` header)
3. **Default fallback** (English)

```javascript
// Frontend
function detectLanguage() {
  // 1. User preference from localStorage/session
  const userLang = localStorage.getItem('preferredLanguage');
  if (userLang) return userLang;

  // 2. Browser language
  const browserLang = navigator.language.split('-')[0]; // 'en-US' -> 'en'

  // 3. Check if supported
  const supportedLangs = ['en', 'es', 'fr', 'de', 'pt', 'zh', 'ar'];
  return supportedLangs.includes(browserLang) ? browserLang : 'en';
}
```

### 5. **Date/Time Localization**

Already have timezone support - extend with locale formatting:

```javascript
// Use Intl API (native browser support)
const formatDate = (date, locale) => {
  return new Intl.DateTimeFormat(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

const formatTime = (date, locale) => {
  return new Intl.DateTimeFormat(locale, {
    hour: 'numeric',
    minute: '2-digit',
    hour12: locale === 'en' // 12h for English, 24h for others
  }).format(date);
};
```

---

## 🌍 Recommended Languages (Priority Order)

### Phase 1: Core Languages (High Demand)
1. **English (en)** - Default ✅
2. **Spanish (es)** - Large church population (Latin America, Spain, US Hispanic)
3. **Portuguese (pt)** - Brazil has massive church community
4. **French (fr)** - Africa, Canada, France

### Phase 2: Asian Languages
5. **Chinese - Simplified (zh-CN)** - China, Singapore
6. **Korean (ko)** - Strong church presence
7. **Tagalog (fil)** - Philippines

### Phase 3: European & Middle East
8. **German (de)** - Germany, Austria, Switzerland
9. **Arabic (ar)** - RTL support, Middle East, North Africa
10. **Russian (ru)** - Russia, Eastern Europe

---

## 📁 Proposed File Structure

```
/home/ubuntu/rostio/
├── locales/
│   ├── en/
│   │   ├── common.json          # Shared UI strings
│   │   ├── auth.json            # Login, signup, invitation
│   │   ├── events.json          # Event management
│   │   ├── schedule.json        # Schedule view
│   │   ├── settings.json        # User settings
│   │   ├── admin.json           # Admin console
│   │   ├── messages.json        # Success/error messages
│   │   └── emails.json          # Email templates
│   ├── es/
│   │   └── [same structure]
│   ├── pt/
│   │   └── [same structure]
│   └── ...
├── frontend/
│   └── js/
│       └── i18n.js              # Frontend i18n manager
└── api/
    └── utils/
        └── i18n.py              # Backend i18n manager
```

---

## 🔧 Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. **Extract all hardcoded strings** to `en/` JSON files
2. **Implement i18n manager** (frontend + backend)
3. **Add language selector** in settings
4. **Update date/time formatting** with locale support

### Phase 2: Core Languages (Week 3-4)
5. **Translate to Spanish & Portuguese** (hire translators or use DeepL API)
6. **Test all workflows** in new languages
7. **Add language switcher** in UI

### Phase 3: Advanced Features (Week 5-6)
8. **RTL support** for Arabic (CSS updates)
9. **Email template localization**
10. **PDF report localization**
11. **Calendar event descriptions** in user's language

### Phase 4: Quality & Expansion (Week 7-8)
12. **Translation management** (consider using Crowdin, Lokalise, or POEditor)
13. **Add more languages** based on user demand
14. **Automated translation testing**

---

## 💡 Best Practices Checklist

### ✅ Development
- [ ] Never hardcode user-facing text
- [ ] Use translation keys consistently (`namespace.section.key`)
- [ ] Store user language preference in database
- [ ] Send `Accept-Language` header in API requests
- [ ] Handle missing translations gracefully (fallback to English)

### ✅ Translation Quality
- [ ] Use professional translators (not just Google Translate)
- [ ] Provide context for translators (screenshots, usage notes)
- [ ] Review translations with native speakers
- [ ] Test UI with longest translations (German text often 30% longer)

### ✅ UX Considerations
- [ ] Allow language switching without page reload
- [ ] Persist language choice across sessions
- [ ] Show language in native script (中文 not "Chinese")
- [ ] Test RTL layouts thoroughly
- [ ] Consider cultural differences (date formats, color meanings)

### ✅ Performance
- [ ] Lazy load translations (only load active language)
- [ ] Cache translation files (browser + CDN)
- [ ] Minimize translation file size (split by feature)
- [ ] Use HTTP/2 for parallel loading

---

## 🛠️ Recommended Tools

### Translation Management Platforms
1. **Crowdin** - Most popular, great GitHub integration
2. **Lokalise** - Developer-friendly, API-first
3. **POEditor** - Affordable, simple
4. **Weblate** - Open source, self-hostable

### Translation Quality
1. **DeepL API** - Best machine translation quality
2. **Google Cloud Translation** - Good balance of quality/cost
3. **Professional translators** - Upwork, Fiverr (for final review)

### Testing
1. **Pseudo-localization** - Test with ████ characters to find hardcoded strings
2. **Automated screenshot comparison** - Catch UI breaks in different languages

---

## 📊 Estimated Effort

### Development Time
- **Foundation setup**: 40-60 hours
- **Extract & organize strings**: 20-30 hours
- **Frontend implementation**: 30-40 hours
- **Backend implementation**: 20-30 hours
- **Testing & QA**: 40-50 hours

**Total**: ~150-210 hours (4-5 weeks for 1 developer)

### Translation Costs (Professional)
- **Per language**: ~$0.10-0.15 per word
- **Estimated words**: ~2,000-3,000
- **Cost per language**: $200-450
- **5 languages**: $1,000-2,250

### Ongoing Maintenance
- **New features**: +20-30% time for i18n
- **Translation updates**: $50-100 per language per update

---

## 🎯 Quick Wins (Start Small)

### Minimal Viable i18n (1 week)
1. **Spanish only** (highest ROI)
2. **UI text only** (no emails/PDFs yet)
3. **Manual language switcher** (no auto-detection)
4. **Basic date formatting**

This gets you 80% of the value with 20% of the effort!

---

## 📝 Next Steps

1. **Approve architecture** (i18next vs custom)
2. **Choose initial languages** (recommend: ES, PT, FR)
3. **Set up translation management** platform
4. **Create string extraction script**
5. **Begin implementation**

Would you like me to start with Phase 1 (Foundation setup)?
