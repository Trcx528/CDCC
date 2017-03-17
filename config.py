prod = {
    'PEEWEE_DATABASE_URI': 'mysql://dev:dev@192.168.48.2:3306/dev',
    'SECRET_KEY': 'fsdakh9809IOJKhfajkkn32480ojkh90p8&*^&^daf',
    'DEBUG': None, # this will cause dev settings to be loaded, set to false to disable
    'TEMPLATES_AUTO_RELOAD': True,

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
