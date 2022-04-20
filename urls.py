def path(endpoint, **kwargs):
    if endpoint == 'main/':
        from viewmodel.main_control import MainControl
        return MainControl(kwargs['user'], kwargs['connection'])
    if endpoint == 'enter/':
        from viewmodel.enter_control import MainControl
        return MainControl()
    if endpoint == 'remote/':
        from viewmodel.remote_control import MainControl
        return MainControl(kwargs['handler'])
