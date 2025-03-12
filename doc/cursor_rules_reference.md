# Cursor Rules Reference

## Important Notice

The cursor rules previously contained in `cursor_rules.md` have been modularized and moved to the `.cursor/rules/` directory for better organization and maintainability.

## Why Modularization?

The rules have been modularized to:

1. **Improve Organization**: Group related rules together for easier reference
2. **Enhance Maintainability**: Allow independent updates to different rule categories
3. **Increase Specificity**: Provide more detailed guidance for specific areas
4. **Enable Better Enforcement**: Make it easier for Cursor to enforce specific rule categories
5. **Support Team Collaboration**: Allow different team members to focus on their areas of expertise

## Rule Files Location

You can find the modular rule files in the `.cursor/rules/` directory:

```
.cursor/rules/
├── README.md                     # Overview of rules structure
├── api_design.md                 # API interface design rules
├── backend_rules.md              # Flask backend rules
├── bitcoin_security.md           # Bitcoin-specific security rules
├── code_review_checklist.md      # Code review checklist
├── coding.md                     # General coding standards
├── deployment.md                 # Deployment guidelines
├── development_setup.md          # Development environment setup
├── frontend_rules.md             # React frontend rules
├── modular_design_principles.md  # Principles for modular architecture
├── python_best_practices.md      # Python best practices
├── security.md                   # General security guidelines
└── testing.md                    # Testing standards
```

## Key Rule Categories

- **Interface Design**: Rules for designing clean interfaces between components (see `api_design.md`)
- **Frontend Development**: Rules for React development (see `frontend_rules.md`)
- **Backend Development**: Rules for Flask development (see `backend_rules.md`)
- **Modular Design**: Principles for creating modular, maintainable code (see `modular_design_principles.md`)
- **Security**: Guidelines for secure development (see `security.md`)

## How to Use These Rules

1. **During Development**: Reference the appropriate rule file for your current task
2. **During Code Review**: Use the `code_review_checklist.md` to verify compliance
3. **For Setup**: Follow `development_setup.md` for environment configuration
4. **For Deployment**: Follow `deployment.md` for deployment procedures

## Rule Updates

If you need to update any rules:

1. Make changes to the appropriate file in `.cursor/rules/`
2. Document your changes in the commit message
3. Get approval through code review
4. Update any related documentation

Remember that all code should adhere to these rules, and exceptions must be explicitly justified in the code. 