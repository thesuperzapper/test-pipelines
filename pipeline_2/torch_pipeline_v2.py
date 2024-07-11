from kfp import __version__ as kfp_version
from kfp import dsl, compiler
from kfp.dsl import Output, Dataset

#########################################################################################
# Init
#########################################################################################
# fail if kfp version is not 2.X.X
if int(kfp_version.split(".")[0]) != 2:
    raise RuntimeError("kfp version == 2.X.X required")


#########################################################################################
# Pipeline
#########################################################################################
@dsl.component(base_image="kubeflownotebookswg/jupyter-pytorch:v1.9.0-rc.0")
def step_1(test_path: Output[Dataset]):
    import torch

    from torchvision.transforms import ToTensor
    from torchvision.datasets import MNIST

    mnist_test = MNIST(".", download=True, train=False, transform=ToTensor())

    with open(test_path.path, "wb") as f:
        torch.save(mnist_test, f)


@dsl.pipeline(
    name="pipeline-1",
    description="pipeline-1 description",
)
def pipeline_3(intro_message: str):
    step_1()


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_3, package_path="torch_pipeline_v2.yaml"
    )

    # from kfp_utils.client_manager import KFPClientManager
    #
    # kfp_client_manager = KFPClientManager(
    #     api_url="https://deploykf.example.com:8443/pipeline",
    #     dex_username="user1@example.com",
    #     dex_password="user1",
    #     dex_auth_type="local",
    #     skip_tls_verify=True,
    # )
    #
    # kfp_client = kfp_client_manager.create_kfp_client()
    #
    # # run the pipeline in v2 mode
    # kfp_client.create_run_from_pipeline_package(
    #     pipeline_file="torch_pipeline_v2.yaml",
    #     arguments={"intro_message": "Hello World!"},
    #     namespace="team-1",
    #     experiment_name="test-v2",
    #     # NOTE: we disable caching to ensure the pipeline is actually run every time
    #     enable_caching=False,
    # )


if __name__ == "__main__":
    main()
