class Module:
    """
    Modules form a tree that store parameters and other
    submodules. They make up the basis of neural network stacks.

    Attributes:
        _modules (dict of name x :class:`Module`): Storage of the child modules
        _parameters (dict of name x :class:`Parameter`): Storage of the module's parameters
        training (bool): Whether the module is in training mode or evaluation mode

    """

    def __init__(self):
        self._modules = {}
        self._parameters = {}
        self.training = True

    def modules(self):
        "Return the direct child modules of this module."
        return self.__dict__["_modules"].values()

    def train(self):
        "Set the mode of this module and all descendent modules to `train`."
        self.training = True
        if self._modules:
            for _ in self._modules:
                module = self._modules[_]
                module.train()

    def eval(self):
        "Set the mode of this module and all descendent modules to `eval`."
        self.training = False
        if self._modules:
            for _ in self._modules:
                module = self._modules[_]
                module.eval()
        # raise NotImplementedError("Need to implement for Task 0.4")

    def named_parameters(self):
        """
        Collect all the parameters of this module and its descendents.

        Returns:
            list of pairs: Contains the name and :class:`Parameter` of each ancestor parameter.
        """

        # print("---------------", self._modules, self._parameters)
        # result = []
        # curr_name = ''
        # print(self._parameters.keys())
        # while self._modules:
        #     for key in self._parameters.items():
        #         result.append((curr_name + key[0], self._parameters[key]))
        #         print(result)
        #         self._parameters.pop(key)
        #         for name, module in list(self._modules.items()):
        #             if module._modules:
        #                 for module in module._modules:
        #                     self.add_parameter(name, module)
        #             self._modules.pop(name)
        # return result
        result = []
        current_name = ""

        def add_children(module, current_name):
            for key in module._parameters:
                result.append((current_name + key, module._parameters[key]))
            if module._modules:
                for name in module._modules:
                    add_children(module._modules[name], current_name + name + ".")

        add_children(self, current_name)
        return result

    def parameters(self):
        parameters_list = []

        def add_parameters(module):
            for key in module._parameters:
                parameter = module._parameters[key]
                parameters_list.append(parameter)
            if module._modules:
                for name in module._modules:
                    add_parameters(module._modules[name])

        add_parameters(self)
        return parameters_list

    def add_parameter(self, k, v):
        """
        Manually add a parameter. Useful helper for scalar parameters.

        Args:
            k (str): Local name of the parameter.
            v (value): Value for the parameter.

        Returns:
            Parameter: Newly created parameter.
        """
        val = Parameter(v, k)
        self.__dict__["_parameters"][k] = val
        return val

    def __setattr__(self, key, val):
        if isinstance(val, Parameter):
            self.__dict__["_parameters"][key] = val
        elif isinstance(val, Module):
            self.__dict__["_modules"][key] = val
        else:
            super().__setattr__(key, val)

    def __getattr__(self, key):
        if key in self.__dict__["_parameters"]:
            return self.__dict__["_parameters"][key]

        if key in self.__dict__["_modules"]:
            return self.__dict__["_modules"][key]

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(self):
        assert False, "Not Implemented"

    def __repr__(self):
        def _addindent(s_, numSpaces):
            s = s_.split("\n")
            if len(s) == 1:
                return s_
            first = s.pop(0)
            s = [(numSpaces * " ") + line for line in s]
            s = "\n".join(s)
            s = first + "\n" + s
            return s

        child_lines = []

        for key, module in self._modules.items():
            mod_str = repr(module)
            mod_str = _addindent(mod_str, 2)
            child_lines.append("(" + key + "): " + mod_str)
        lines = child_lines

        main_str = self.__class__.__name__ + "("
        if lines:
            # simple one-liner info, which most builtin Modules will use
            main_str += "\n  " + "\n  ".join(lines) + "\n"

        main_str += ")"
        return main_str


class Parameter:
    """
    A Parameter is a special container stored in a :class:`Module`.

    It is designed to hold a :class:`Variable`, but we allow it to hold
    any value for testing.
    """

    def __init__(self, x=None, name=None):
        self.value = x
        self.name = name
        if hasattr(x, "requires_grad_"):
            self.value.requires_grad_(True)
            if self.name:
                self.value.name = self.name

    def update(self, x):
        "Update the parameter value."
        self.value = x
        if hasattr(x, "requires_grad_"):
            self.value.requires_grad_(True)
            if self.name:
                self.value.name = self.name

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)
