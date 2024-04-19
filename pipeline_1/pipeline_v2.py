from kfp import __version__ as kfp_version
from kfp import dsl, compiler

#########################################################################################
# Init
#########################################################################################
# fail if kfp version is not 2.X.X
if int(kfp_version.split(".")[0]) != 2:
    raise RuntimeError("kfp version == 2.X.X required")


#########################################################################################
# Pipeline
#########################################################################################
@dsl.component(base_image="python:3.10")
def step_1(
    intro_message: str,
    # TODO: figure out how to use dsl.InputPath to pass large strings
    #       https://github.com/kubeflow/pipelines/issues/10378#issuecomment-2067201647
    text: str,
    output_file: dsl.Output[dsl.Artifact],
):
    print(intro_message)
    print(text)

    with open(output_file.path, "w") as f:
        f.write(text)


@dsl.pipeline(
    name="pipeline-1",
    # TODO: for some reason the KFP v1 UI will accept this pipeline,
    #       as long as no description is provided
    description="pipeline-1 description",
)
def pipeline_1(intro_message: str):
    step_1(intro_message=intro_message, text="1\n" * 100)


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_1, package_path="pipeline_v2.yaml"
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
    #     pipeline_file="pipeline_v2.yaml",
    #     arguments={"intro_message": "Hello World!"},
    #     namespace="team-1",
    #     experiment_name="test-v2",
    #     # NOTE: we disable caching to ensure the pipeline is actually run every time
    #     enable_caching=False,
    # )


if __name__ == "__main__":
    main()
