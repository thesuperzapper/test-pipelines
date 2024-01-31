from kfp_utils.client_manager import KFPClientManager

# CONFIGS (default)
kfp_api_url = "https://deploykf.example.com:8443/pipeline"
kfp_namespace = "team-1"
dex_username = "user1@example.com"
dex_password = "user1"

# initialize a KFPClientManager
kfp_client_manager = KFPClientManager(
    api_url=kfp_api_url,
    dex_username=dex_username,
    dex_password=dex_password,
    dex_auth_type="local",
    skip_tls_verify=True,
)

# get a newly authenticated KFP client
# TIP: long-lived sessions might need to get a new client when their session expires
kfp_client = kfp_client_manager.create_kfp_client()

# test the client by listing experiments
experiments = kfp_client.list_experiments(namespace=kfp_namespace)
print(experiments)
