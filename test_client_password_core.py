from kfp_utils.client_manager import KFPClientManager

# initialize a KFPClientManager
kfp_client_manager = KFPClientManager(
    api_url="http://localhost:8080/pipeline",
    dex_username="user@example.com",
    dex_password="12341234",
    dex_auth_type="local",
    skip_tls_verify=True,
)

# get a newly authenticated KFP client
# TIP: long-lived sessions might need to get a new client when their session expires
kfp_client = kfp_client_manager.create_kfp_client()

# test the client by listing experiments
experiments = kfp_client.list_experiments(namespace="kubeflow-user-example-com")
print(experiments)
