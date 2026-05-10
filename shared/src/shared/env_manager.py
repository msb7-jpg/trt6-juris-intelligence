import os


class EnviromentManager:

    def get_with_default(self, variable_name: str, default_value: str = None) -> str:
        value = os.getenv(variable_name)
        if value is None and default_value is not None:
            return default_value

        if value is None:
            raise ValueError(f"Environment variable '{variable_name}' not found.")

        return value

    def get_lmstudio_base_url(self) -> str:
        return self.get_with_default("LMSTUDIO_API_URL", "http://172.26.67.165:1234/v1")

    def get_lmstudio_api_key(self) -> str:
        return self.get_with_default("LMSTUDIO_API_KEY", "lm-studio")

    def get_lmstudio_model(self) -> str:
        return self.get_with_default("LMSTUDIO_MODEL", "google/gemma-3-4b")

    def get_log_errors(self):
        return (
            self.get_with_default("LOG_ERRORS", "false")
                .strip()
                .lower() in {"1", "true", "yes", "on"}
        )
