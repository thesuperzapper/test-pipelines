import kfp

from kfp_utils.credentials_oob import DeployKFCredentialsOutOfBand


# initialize a credentials instance
credentials = DeployKFCredentialsOutOfBand(
    issuer_url="https://deploykf.example.com:8443/dex",
    skip_tls_verify=True,
)


# creates a patched client that supports disabling SSL verification
# required before kfp v2: https://github.com/kubeflow/pipelines/pull/7174
def patched_kfp_client(verify_ssl=True):
    _original_load_config = kfp.Client._load_config

    def _patched_load_config(client_self, *args, **kwargs):
        config = _original_load_config(client_self, *args, **kwargs)
        config.verify_ssl = verify_ssl
        return config

    _patched_client = kfp.Client
    _patched_client._load_config = _patched_load_config

    return _patched_client


# initialize a client instance
kfp_client = patched_kfp_client(verify_ssl=not credentials.skip_tls_verify)(
    host="https://deploykf.example.com:8443/pipeline",
    credentials=credentials,
)

# test the client by listing experiments
experiments = kfp_client.list_experiments(namespace="team-1")
print(experiments)
