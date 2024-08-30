from enum import Enum


class EnvType(Enum):
    DEV = "Dev"
    STAGING = "Staging"
    PROD = "Prod"


class EnvConf:
    def __init__(
        self,
        env_type: EnvType,
        env_name: str,
        account: str,
        region: str,
        resource_prefix: str,
    ):
        self._env_type = env_type
        self._env_name = env_name
        self._account = account
        self._region = region
        self._resource_prefix = resource_prefix

    @property
    def env_type(self):
        return self._env_type

    @property
    def env_name(self):
        return self._env_name

    @property
    def account(self):
        return self._account

    @property
    def region(self):
        return self._region

    @property
    def bucket_prefix(self):
        return self._bucket_prefix

    @property
    def resource_prefix(self):
        return self._resource_prefix

    def _get_by_env_name(self, d: dict) -> any:
        if self._env_name in d:
            return d[self._env_name]
        else:
            return d["Default"]


class PipelineConf:

    RESOURCE_PREFIX_DEFAULT = "test"

    def __init__(
        self,
        name: str,
        env_confs: list[EnvConf],
        repo: str,
        branch: str,
        connection_arn: str,
    ):
        self._name = name
        self._env_confs = env_confs
        self._repo = repo
        self._branch = branch
        self._connection_arn = connection_arn

    @property
    def name(self):
        return self._name

    @property
    def env_confs(self):
        return self._env_confs

    @property
    def repo(self):
        return self._repo

    @property
    def branch(self):
        return self._branch

    @property
    def connection_arn(self):
        return self._connection_arn
