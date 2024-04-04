import toml

def load_twitch_credentials() -> dict[str, str]:
    config = toml.load("./cfg/secrets.toml")
    return {
        "client_id": config["twitch"]["client_id"],
        "client_secret": config["twitch"]["client_secret"]
    }
