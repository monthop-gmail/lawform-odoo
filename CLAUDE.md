# CLAUDE.md — Project Guide for AI Agents

## Project Overview

Odoo module `legal_forms` — Thai court form management system.
Generates PDF court documents with auto-filled data from case records.

- **Odoo version**: 19.0 (branch `19.0`), also maintained on `18.0`
- **Module path**: `/legal_forms/`
- **Database**: `lawform`
- **Test URL**: http://localhost:8069 (admin/admin)

## Branch Strategy

| Branch | Purpose | Odoo Version |
|--------|---------|-------------|
| `19.0` | **Primary development** — matches running Odoo | 19.0 |
| `18.0` | Backport / legacy support | 18.0 (manifest version only) |
| `main` | Documentation only — NOT for module code | — |

**Rule**: Develop on `19.0`, cherry-pick to `18.0` when needed. Never merge between them directly.

## Architecture

```
legal_forms/
  models/
    legal_case.py        — คดีความ (case record)
    form_template.py     — แบบฟอร์ม template (HTML + placeholders)
    form_document.py     — เอกสาร instance (merged data)
    res_partner.py       — extend res.partner (race, nationality, etc.)
    continuous_text.py   — ข้อความต่อเนื่อง 40 ก.
    witness_list.py      — บัญชีพยาน
    text_annotation.py   — ข้อความแทรกอิสระ
    printer_config.py    — ตั้งค่าเครื่องพิมพ์
    thai_utils.py        — Thai date/digits/baht text (pure functions)
  data/
    form_template_data.xml  — 92 court form templates (noupdate=1)
    form_category_data.xml  — 10 form categories
  views/  reports/  security/
```

## Merge Field System (Placeholder)

- **Syntax**: `%(field_name)s` in template HTML
- **Engine**: `FormDocument._apply_merge_fields()` — simple string replace
- **Currently supports 49 placeholders** (see form_document.py)
- **IMPORTANT**: `body_html` fields use `sanitize=False` — Odoo's HTML sanitizer strips `%(...)s` patterns

### Placeholder naming convention

```
%(role)s                    — name (e.g. plaintiff, defendant, lawyer, agent, guarantor)
%(role_address)s            — formatted address
%(role_phone)s              — phone number
%(role_email)s              — email
%(role_id_no)s              — national ID (vat field)
%(role_race)s               — race
%(role_nationality)s        — nationality
%(role_occupation)s         — occupation
%(role_age)s                — computed age (Thai digits)
%(role_birthdate)s          — birthdate (Thai long format)
%(role_fax)s                — fax number
%(role_birthdate)s          — birthdate (Thai long format)
%(lawyer_license_no)s       — lawyer license number
%(case_category)s           — case category text
%(charge)s                  — charge/offense
%(claim_amount)s            — amount (formatted number)
%(claim_amount_text)s       — amount in Thai words
%(judgment_date)s           — judgment date (Thai long format)
%(judgment_read_date)s      — judgment read date
%(bail_amount)s             — bail amount (formatted)
%(bail_amount_text)s        — bail amount in Thai words
%(written_location)s        — document written location
%(date_long)s               — Thai date long format
%(date_short)s              — Thai date short format
%(thai_year)s               — Buddhist era year
```

## Form Template Status

**20 of 92 forms** have placeholders. See `FORM_TRACKING.md` for full list.

Forms with placeholders (lawyer-facing, commonly used):
- แบบ ๑ มอบอำนาจ, แบบ ๔ คำฟ้อง, แบบ ๕ ท้ายฟ้องแพ่ง, แบบ ๖ ท้ายฟ้องอาญา
- แบบ ๗ คำร้อง, แบบ ๙ ใบแต่งทนาย, แบบ ๑๐ มอบฉันทะ, แบบ ๑๑ คำให้การจำเลย
- แบบ ๓๒-๓๙ อุทธรณ์/ฎีกา ทั้งชุด
- แบบ ๑๕ บัญชีพยาน, แบบ ๒๙ ประนีประนอม, แบบ ๓๒ อุทธรณ์
- แบบ ๕๗ ขอปล่อยชั่วคราว, แบบ ๕๘ สัญญาประกัน

Remaining 79 forms are mostly court-internal (summons, warrants, receipts) — still have `...........` dots.

## Critical Rules

### DO
- Use `sanitize=False` on any `fields.Html` that stores placeholders
- Use `%(name)s` syntax for all merge field placeholders
- Use `to_thai_digits()` for any number shown in Thai
- Use `num_to_thai_text()` for money amounts in words
- Run `docker exec lawform-odoo-1 odoo --config=/workspace/.devcontainer/odoo.conf -d lawform -u legal_forms --stop-after-init --no-http` to update module
- After updating, `docker restart lawform-odoo-1`
- When updating template data, temporarily set `noupdate="0"` in XML, update, then set back to `"1"`

### DON'T
- Don't use `expand="0"` or `string=` on `<group>` in search views (removed in Odoo 19)
- Don't add `domain="[]"` is **required** on group-by filters in search views (Odoo 19)
- Don't forget to add new model files to `models/__init__.py`
- Don't forget to add new view files to `__manifest__.py`
- Don't use Odoo default config (`/etc/odoo/odoo.conf`) — always use `/workspace/.devcontainer/odoo.conf`

## Testing

```bash
# Update module
docker exec lawform-odoo-1 odoo --config=/workspace/.devcontainer/odoo.conf \
  -d lawform -u legal_forms --stop-after-init --no-http

# Restart
docker restart lawform-odoo-1

# Quick field check via XML-RPC
docker exec lawform-odoo-1 python3 -c "
import xmlrpc.client
url = 'http://localhost:8069'
db = 'lawform'
uid = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common').authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
# ... use models.execute_kw() ...
"
```

## Commit Convention

```
<verb> <what> (short, imperative)

<details if needed>

Co-Authored-By: <agent name> <noreply@anthropic.com>
```
