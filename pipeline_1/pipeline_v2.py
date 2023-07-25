from kfp import dsl, compiler
from kfp import __version__ as kfp_version

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
        pipeline_func=pipeline_1, package_path="pipeline_v2.yaml"
    )


if __name__ == "__main__":
    main()
