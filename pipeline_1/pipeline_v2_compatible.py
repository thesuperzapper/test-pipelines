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
def step_1(text: str, output_file: dsl.Output[dsl.Artifact]):
    print(text)

    with open(output_file.path, "w") as f:
        f.write(text)


@dsl.pipeline(name="pipeline-1", description="pipeline-1 description")
def pipeline_1():
    step_1(text="1\n" * 100)


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_1, package_path="pipeline_v2_compatible.json"
    )


if __name__ == "__main__":
    main()
