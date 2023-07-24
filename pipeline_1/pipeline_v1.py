from kfp import dsl, compiler, components
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
def step_1(text: components.InputPath(str)):
    print(text)


step_1__op = components.create_component_from_func(
    func=step_1, base_image="python:3.10"
)


@dsl.pipeline(name="pipeline_1", description="pipeline_1 description")
def pipeline_1():
    step_1__op(text="1\n" * 100)


#########################################################################################
# Main
#########################################################################################
def main():
    compiler.Compiler().compile(
        pipeline_func=pipeline_1, package_path="pipeline_v1.yaml"
    )


if __name__ == "__main__":
    main()
