class ModeNotSet(Exception):
  def __init__(self, message):
    super().__init__(message)


class InvalidModeError(Exception):
  def __init__(self, message):
    super().__init__(message)


class DotEnvNotFound(Exception):
  def __init__(self, message):
    super().__init__(message)


