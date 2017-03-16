

prod = {
    'PEEWEE_DATABASE_URI': 'sqlite:///app.db',
    'SECRET_KEY': 'changeme',
    'DEBUG': None
    }


# dev will inherit all settings from prod that it does not override
dev = {
    'DEBUG_TB_PANELS': [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        'flask_pw.debugtoolbar.PeeweeDebugPanel'
        ],
    'DEBUG_TB_INTERCEPT_REDIRECTS': False
    }
