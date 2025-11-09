def smart_function(**kwargs):
    name = kwargs.get('name', 'Anonymous')

    if 'age' in kwargs:
        print(f"Age: {kwargs['age']}")

    if "ref" in kwargs:
        print(f"Ref Code: {kwargs["ref"]}")

    for key, value in kwargs.items():
        print(f"{key}: {value}")


smart_function(name="John", age=25, city="NYC", ref=12345)