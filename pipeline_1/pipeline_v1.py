from kfp import __version__ as kfp_version
from kfp import dsl, compiler, components

#########################################################################################
# Init
#########################################################################################
# fail if kfp version is not 1.X.X
if int(kfp_version.split(".")[0]) != 1:
    raise RuntimeError("kfp version == 1.X.X required")


#########################################################################################
# Pipeline
#########################################################################################
def step_1(intro_message: str, text: components.InputPath(str)):
    print(intro_message)
    print(text)


step_1__op = components.create_component_from_func(
    func=step_1, base_image="python:3.10"
)


@dsl.pipeline(name="pipeline_1", description="pipeline_1 description")
def pipeline_1(intro_message: str):
    step_1__op(intro_message=intro_message, text="1\n" * 100)


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_1, package_path="pipeline_v1.yaml"
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
    # # run the pipeline
    # kfp_client.create_run_from_pipeline_package(
    #     pipeline_file="pipeline_v1.yaml",
    #     arguments={"intro_message": "Hello World!"},
    #     namespace="team-1",
    #     experiment_name="test-v1",
    # )


if __name__ == "__main__":
    main()
