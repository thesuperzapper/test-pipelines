from kfp.v2 import dsl, compiler
from kfp import __version__ as kfp_version

#########################################################################################
# Init
#########################################################################################
# fail if kfp version is not 1.X.X
if int(kfp_version.split(".")[0]) != 1:
    raise RuntimeError("kfp version == 1.X.X required")


#########################################################################################
# Pipeline
#########################################################################################
@dsl.component(base_image="python:3.10")
def step_1(
    intro_message: str,
    # TODO: figure out how to use dsl.InputPath to pass large strings
    text: str,
    output_file: dsl.Output[dsl.Artifact],
):
    print(intro_message)
    print(text)

    with open(output_file.path, "w") as f:
        f.write(text)


@dsl.pipeline(name="pipeline-1", description="pipeline-1 description")
def pipeline_1(intro_message: str):
    step_1(intro_message=intro_message, text="1\n" * 100)


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_1, package_path="pipeline_v2_compatible.json"
    )

    # from kfp_utils.client_manager import KFPClientManager
    # import kfp
    #
    # kfp_client_manager = KFPClientManager(
    #     api_url="https://deploykf.example.com:8443/pipeline",
    #     dex_username="user1@example.com",
    #     dex_password="user1",
    #     dex_auth_type="local",
    #     skip_tls_verify=True,
    # )
    #
    # kfp_client = kfp_client_manager.get_kfp_client()
    #
    # # run the pipeline in v2 compatibility mode
    # # NOTE: we are running the function, not the compiled pipeline JSON
    # kfp_client.create_run_from_pipeline_func(
    #     pipeline_func=pipeline_1,
    #     arguments={"intro_message": "Hello World!"},
    #     mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
    #     namespace="team-1",
    #     experiment_name="test-v2",
    # )


if __name__ == "__main__":
    main()
