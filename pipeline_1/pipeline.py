from kfp import dsl, compiler, components


def step_1(text: components.InputPath(str)):
    print(text)


step_1__op = components.create_component_from_func(
    func=step_1, base_image="python:3.10"
)


@dsl.pipeline(name="pipeline_1", description="pipeline_1 description")
def pipeline_1():
    step_1__op(text="1\n" * 100)


def main():
    compiler.Compiler().compile(pipeline_func=pipeline_1, package_path="pipeline.yaml")


if __name__ == "__main__":
    main()
