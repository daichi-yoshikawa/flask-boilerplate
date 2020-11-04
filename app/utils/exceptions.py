class ModeNotSet(Exception):
  def __init__(self, message):
    super().__init__(message)


class InvalidModeError(Exception):
  def __init__(self, message):
    super().__init__(message)


class DotEnvNotFound(Exception):
  def __init__(self, message):
    super().__init__(message)


class ApiException(Exception):
  def __init__(self, message, status):
    super().__init__(message)
    self.status = status
