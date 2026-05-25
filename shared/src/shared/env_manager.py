import os


class EnviromentManager:

    def get_with_default(self, variable_name: str, default_value: str = None) -> str:
        value = os.getenv(variable_name)
        if value is None and default_value is not None:
            return default_value

        if value is None:
            raise ValueError(f"Environment variable '{variable_name}' not found.")

        return value

    def get_datajud_api_url(self) -> str:
        return self.get_with_default("DATAJUD_API_URL", "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search")

    def get_lmstudio_base_url(self) -> str:
        return self.get_with_default("LMSTUDIO_API_URL", "http://host.docker.internal:1234/v1")

    def get_lmstudio_api_key(self) -> str:
        return self.get_with_default("LMSTUDIO_API_KEY", "lm-studio")

    def get_lmstudio_model(self) -> str:
        return self.get_with_default("LMSTUDIO_MODEL", "expert/trt6-model") # Facade name

    def get_api_base_url(self) -> str:
        return self.get_with_default("API_BASE_URL", "http://api:8000")

    def get_log_errors(self):
        return (
            self.get_with_default("LOG_ERRORS", "false")
                .strip()
                .lower() in {"1", "true", "yes", "on"}
        )
