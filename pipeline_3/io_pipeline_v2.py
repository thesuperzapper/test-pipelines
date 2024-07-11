from kfp import __version__ as kfp_version
from kfp import dsl, compiler
from kfp.dsl import OutputPath, InputPath

#########################################################################################
# Init
#########################################################################################
# fail if kfp version is not 2.X.X
if int(kfp_version.split(".")[0]) != 2:
    raise RuntimeError("kfp version == 2.X.X required")


#########################################################################################
# Pipeline
#########################################################################################
@dsl.component(base_image="python:3.11")
def data_get(dataset: OutputPath("dataset")):
    print("Running this")

    with open(dataset, "w") as f:
        f.write("Hello, world!")


@dsl.component(base_image="python:3.11")
def preprocess(input: InputPath("dataset")):
    with open(input, "r") as f:
        print(f.read())


@dsl.pipeline(
    name="pipeline-3",
    description="pipeline-3 description",
)
def pipeline_3():
    data_get_op = data_get()
    preprocess_op = preprocess(input=data_get_op.outputs["dataset"])


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_3, package_path="io_pipeline_v2.yaml"
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
    #     pipeline_file="io_pipeline_v2.yaml",
    #     arguments={},
    #     namespace="team-1",
    #     experiment_name="test-v2",
    #     # NOTE: we disable caching to ensure the pipeline is actually run every time
    #     enable_caching=False,
    # )


if __name__ == "__main__":
    main()
