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
def markdown_vis(mlpipeline_ui_metadata_path: components.OutputPath()):
    import json

    metadata = {
        "outputs": [
            {
                "storage": "inline",
                "source": "Inline Markdown - Hello Metrics World",
                "type": "markdown",
            }
        ]
    }

    with open(mlpipeline_ui_metadata_path, "w") as metadata_file:
        json.dump(metadata, metadata_file)


markdown_vis__op = components.create_component_from_func(
    func=markdown_vis, base_image="python:3.10"
)


@dsl.pipeline(
    name="testing out metrics and their visualizations",
    description="testing out metrics and their visualizations",
)
def viz_pipeline_1():
    task_1 = markdown_vis__op()
    task_1.execution_options.caching_strategy.max_cache_staleness = "P0D"


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=viz_pipeline_1, package_path="viz_pipeline_v1.yaml"
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
    #     pipeline_file="viz_pipeline_v1.yaml",
    #     arguments={},
    #     namespace="team-1",
    #     experiment_name="test-v1",
    # )


if __name__ == "__main__":
    main()
