"""Original source: https://gist.githubusercontent.com/Maximilian-Winter/5373962ef456a2b0d1ae324fb78e623e/raw/8d4bcaecb55e30edd645086422697887d93283f9/gbnf_grammar_generator.py"""
import inspect
import json
import re
import typing
from inspect import isclass, getdoc
from types import NoneType

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from typing import Any, Type, List, get_args, get_origin, Tuple, Union, Optional
from enum import Enum

import re


class PydanticDataType(Enum):
    """
    Defines the data types supported by Pydantic.

    Attributes:
        STRING (str): Represents a string data type.
        BOOLEAN (str): Represents a boolean data type.
        INTEGER (str): Represents an integer data type.
        FLOAT (str): Represents a float data type.
        OBJECT (str): Represents an object data type.
        ARRAY (str): Represents an array data type.
        ENUM (str): Represents an enum data type.
        CUSTOM_CLASS (str): Represents a custom class data type.
    """
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    OBJECT = "object"
    ARRAY = "array"
    ENUM = "enum"
    CUSTOM_CLASS = "custom-class"


def map_pydantic_type_to_gbnf(pydantic_type: Type[Any]) -> str:
    if isclass(pydantic_type) and issubclass(pydantic_type, str):
        return PydanticDataType.STRING.value
    elif isclass(pydantic_type) and issubclass(pydantic_type, bool):
        return PydanticDataType.BOOLEAN.value
    elif isclass(pydantic_type) and issubclass(pydantic_type, int):
        return PydanticDataType.INTEGER.value
    elif isclass(pydantic_type) and issubclass(pydantic_type, float):
        return PydanticDataType.FLOAT.value
    elif isclass(pydantic_type) and issubclass(pydantic_type, Enum):
        return PydanticDataType.ENUM.value
    elif isclass(pydantic_type) and issubclass(pydantic_type, BaseModel):
        return format_model_and_field_name(pydantic_type.__name__)
    elif get_origin(pydantic_type) == list:
        element_type = get_args(pydantic_type)[0]
        return f"{map_pydantic_type_to_gbnf(element_type)}-list"
    elif get_origin(pydantic_type) == Union:
        union_types = get_args(pydantic_type)
        union_rules = [map_pydantic_type_to_gbnf(ut) for ut in union_types]
        return f"union-{'-or-'.join(union_rules)}"
    elif get_origin(pydantic_type) == Optional:
        element_type = get_args(pydantic_type)[0]
        return f"optional-{map_pydantic_type_to_gbnf(element_type)}"
    elif isclass(pydantic_type):
        return f"{PydanticDataType.CUSTOM_CLASS.value}-{format_model_and_field_name(pydantic_type.__name__)}"
    elif get_origin(pydantic_type) == dict:
        key_type, value_type = get_args(pydantic_type)
        return f"custom-dict-key-type-{format_model_and_field_name(map_pydantic_type_to_gbnf(key_type))}-value-type-{format_model_and_field_name(map_pydantic_type_to_gbnf(value_type))}"
    else:
        return "unknown"


def format_model_and_field_name(model_name: str) -> str:
    parts = re.findall('[A-Z][^A-Z]*', model_name)
    if not parts:  # Check if the list is empty
        return model_name.lower().replace("_", "-")
    return '-'.join(part.lower().replace("_", "-") for part in parts)


def generate_list_rule(element_type):
    """
    Generate a GBNF rule for a list of a given element type.

    :param element_type: The type of the elements in the list (e.g., 'string').
    :return: A string representing the GBNF rule for a list of the given type.
    """
    rule_name = f"{map_pydantic_type_to_gbnf(element_type)}-list"
    element_rule = map_pydantic_type_to_gbnf(element_type)
    list_rule = f"{rule_name} ::= \"[\" ws ( {element_rule} (\",\" ws {element_rule})*  )? \"]\""
    return list_rule


def get_members_structure(cls, rule_name):
    if issubclass(cls, Enum):
        # Handle Enum types
        members = [f'\"\\\"{member.value}\\\"\"' for name, member in cls.__members__.items()]
        return f"{cls.__name__.lower()} ::= " + " | ".join(members)
    if cls.__annotations__ and cls.__annotations__ != {}:
        result = f'{rule_name} ::= "{{"'
        type_list_rules = []
        # Modify this comprehension
        members = [f' ws \"\\\"{name}\\\"\" ws ":" ws {map_pydantic_type_to_gbnf(param_type)}'
                   for name, param_type in cls.__annotations__.items()
                   if name != 'self']

        result += '", "'.join(members)
        result += ' ws "}"'
        return result, type_list_rules
    else:
        init_signature = inspect.signature(cls.__init__)
        parameters = init_signature.parameters
        result = f'{cls.__name__.lower()} ::= "{{"'
        type_list_rules = []
        # Modify this comprehension too
        members = [f' ws \"\\\"{name}\\\"\" ws ":" ws {map_pydantic_type_to_gbnf(param.annotation)}'
                   for name, param in parameters.items()
                   if name != 'self' and param.annotation != inspect.Parameter.empty]

        result += '", "'.join(members)
        result += ' ws "}"'
        return result, type_list_rules


def regex_to_gbnf(regex_pattern: str) -> str:
    """
    Translate a basic regex pattern to a GBNF rule.
    Note: This function handles only a subset of simple regex patterns.
    """
    gbnf_rule = regex_pattern

    # Translate common regex components to GBNF
    gbnf_rule = gbnf_rule.replace('\\d', '[0-9]')
    gbnf_rule = gbnf_rule.replace('\\s', '[ \t\n]')

    # Handle quantifiers and other regex syntax that is similar in GBNF
    # (e.g., '*', '+', '?', character classes)

    return gbnf_rule


def generate_gbnf_integer_rules(max_digit=None, min_digit=None):
    """

    Generate GBNF Integer Rules

    Generates GBNF (Generalized Backus-Naur Form) rules for integers based on the given maximum and minimum digits.

    Parameters:
    - max_digit (int): The maximum number of digits for the integer. Default is None.
    - min_digit (int): The minimum number of digits for the integer. Default is None.

    Returns:
    - integer_rule (str): The identifier for the integer rule generated.
    - additional_rules (list): A list of additional rules generated based on the given maximum and minimum digits.

    """
    additional_rules = []

    # Define the rule identifier based on max_digit and min_digit
    integer_rule = "integer-part"
    if max_digit is not None:
        integer_rule += f"-max{max_digit}"
    if min_digit is not None:
        integer_rule += f"-min{min_digit}"

    # Handling Integer Rules
    if max_digit is not None or min_digit is not None:
        # Start with an empty rule part
        integer_rule_part = ''

        # Add mandatory digits as per min_digit
        if min_digit is not None:
            integer_rule_part += '[0-9] ' * min_digit

        # Add optional digits up to max_digit
        if max_digit is not None:
            optional_digits = max_digit - (min_digit if min_digit is not None else 0)
            integer_rule_part += ''.join(['[0-9]? ' for _ in range(optional_digits)])

        # Trim the rule part and append it to additional rules
        integer_rule_part = integer_rule_part.strip()
        if integer_rule_part:
            additional_rules.append(f'{integer_rule} ::= {integer_rule_part}')

    return integer_rule, additional_rules


def generate_gbnf_float_rules(max_digit=None, min_digit=None, max_precision=None, min_precision=None):
    """
    Generate GBNF float rules based on the given constraints.

    :param max_digit: Maximum number of digits in the integer part (default: None)
    :param min_digit: Minimum number of digits in the integer part (default: None)
    :param max_precision: Maximum number of digits in the fractional part (default: None)
    :param min_precision: Minimum number of digits in the fractional part (default: None)
    :return: A tuple containing the float rule and additional rules as a list

    Example Usage:
    max_digit = 3
    min_digit = 1
    max_precision = 2
    min_precision = 1
    generate_gbnf_float_rules(max_digit, min_digit, max_precision, min_precision)

    Output:
    ('float-3-1-2-1', ['integer-part-max3-min1 ::= [0-9] [0-9] [0-9]?', 'fractional-part-max2-min1 ::= [0-9] [0-9]?', 'float-3-1-2-1 ::= integer-part-max3-min1 "." fractional-part-max2-min
    *1'])

    Note:
    GBNF stands for Generalized Backus-Naur Form, which is a notation technique to specify the syntax of programming languages or other formal grammars.
    """
    additional_rules = []

    # Define the integer part rule
    integer_part_rule = "integer-part" + (f"-max{max_digit}" if max_digit is not None else "") + (
        f"-min{min_digit}" if min_digit is not None else "")

    # Define the fractional part rule based on precision constraints
    fractional_part_rule = "fractional-part"
    fractional_rule_part = ''
    if max_precision is not None or min_precision is not None:
        fractional_part_rule += (f"-max{max_precision}" if max_precision is not None else "") + (
            f"-min{min_precision}" if min_precision is not None else "")
        # Minimum number of digits
        fractional_rule_part = '[0-9]' * (min_precision if min_precision is not None else 1)
        # Optional additional digits
        fractional_rule_part += ''.join([' [0-9]?'] * (
            (max_precision - (min_precision if min_precision is not None else 1)) if max_precision is not None else 0))
        additional_rules.append(f'{fractional_part_rule} ::= {fractional_rule_part}')

    # Define the float rule
    float_rule = f"float-{max_digit if max_digit is not None else 'X'}-{min_digit if min_digit is not None else 'X'}-{max_precision if max_precision is not None else 'X'}-{min_precision if min_precision is not None else 'X'}"
    additional_rules.append(f'{float_rule} ::= {integer_part_rule} "." {fractional_part_rule}')

    # Generating the integer part rule definition, if necessary
    if max_digit is not None or min_digit is not None:
        integer_rule_part = '[0-9]'
        if min_digit is not None and min_digit > 1:
            integer_rule_part += ' [0-9]' * (min_digit - 1)
        if max_digit is not None:
            integer_rule_part += ''.join([' [0-9]?'] * (max_digit - (min_digit if min_digit is not None else 1)))
        additional_rules.append(f'{integer_part_rule} ::= {integer_rule_part.strip()}')

    return float_rule, additional_rules


def generate_gbnf_rule_for_type(model_name, field_name, field_type, is_optional, processed_models, created_rules,
                                field_info=None) -> \
        Tuple[str, list]:
    """
    Generate GBNF rule for a given field type.

    :param model_name: Name of the model.
    :param field_name: Name of the field.
    :param field_type: Type of the field.
    :param is_optional: Whether the field is optional.
    :param processed_models: List of processed models.
    :param created_rules: List of created rules.
    :param field_info: Additional information about the field (optional).

    :return: Tuple containing the GBNF type and a list of additional rules.
    :rtype: Tuple[str, list]
    """
    rules = []

    field_name = format_model_and_field_name(field_name)
    gbnf_type = map_pydantic_type_to_gbnf(field_type)

    if isclass(field_type) and issubclass(field_type, BaseModel):
        nested_model_name = format_model_and_field_name(field_type.__name__)
        nested_model_rules = generate_gbnf_grammar(field_type, processed_models, created_rules)
        rules.extend(nested_model_rules)
        gbnf_type, rules = nested_model_name, rules
    elif isclass(field_type) and issubclass(field_type, Enum):
        enum_values = [f'\"\\\"{e.value}\\\"\"' for e in field_type]  # Adding escaped quotes
        enum_rule = f"{model_name}-{field_name} ::= {' | '.join(enum_values)}"
        rules.append(enum_rule)
        gbnf_type, rules = model_name + "-" + field_name, rules
    elif get_origin(field_type) == list:  # Array
        element_type = get_args(field_type)[0]
        element_rule_name, additional_rules = generate_gbnf_rule_for_type(model_name, f"{field_name}-element",
                                                                          element_type, is_optional, processed_models,
                                                                          created_rules)
        rules.extend(additional_rules)
        array_rule = f"""{model_name}-{field_name} ::= "[" ws {element_rule_name} ("," ws {element_rule_name})* ws "]" """
        rules.append(array_rule)
        gbnf_type, rules = model_name + "-" + field_name, rules
    elif gbnf_type.startswith("custom-class-"):
        nested_model_rules, field_types = get_members_structure(field_type, gbnf_type)
        rules.append(nested_model_rules)
    elif gbnf_type.startswith("custom-dict-"):
        key_type, value_type = get_args(field_type)

        additional_key_type, additional_key_rules = generate_gbnf_rule_for_type(model_name, f"{field_name}-key-type",
                                                                                key_type, is_optional, processed_models,
                                                                                created_rules)
        additional_value_type, additional_value_rules = generate_gbnf_rule_for_type(model_name,
                                                                                    f"{field_name}-value-type",
                                                                                    value_type, is_optional,
                                                                                    processed_models, created_rules)
        gbnf_type = fr'{gbnf_type} ::= "{{" ws ( {additional_key_type} ":" ws {additional_value_type} ("," ws {additional_key_type} ":" ws {additional_value_type})*  )? "}}" ws'

        rules.extend(additional_key_rules)
        rules.extend(additional_value_rules)
    elif gbnf_type.startswith("union-"):
        union_types = get_args(field_type)
        union_rules = []

        for union_type in union_types:
            if not issubclass(union_type, NoneType):
                union_gbnf_type, union_rules_list = generate_gbnf_rule_for_type(model_name, field_name, union_type,
                                                                                False,
                                                                                processed_models, created_rules)
                union_rules.append(union_gbnf_type)
                rules.extend(union_rules_list)

        # Defining the union grammar rule separately
        if len(union_rules) == 1:
            union_grammar_rule = f"{model_name}-{field_name}-optional ::= ({' | '.join(union_rules)})?"
        else:
            union_grammar_rule = f"{model_name}-{field_name}-union ::= {' | '.join(union_rules)}"
        rules.append(union_grammar_rule)
        if len(union_rules) == 1:
            gbnf_type = f"{model_name}-{field_name}-optional"
        else:
            gbnf_type = f"{model_name}-{field_name}-union"
    elif isclass(field_type) and issubclass(field_type, str):
        if field_info and hasattr(field_info, 'pattern'):
            # Convert regex pattern to grammar rule
            regex_pattern = field_info.regex.pattern
            gbnf_type = f"pattern-{field_name} ::= {regex_to_gbnf(regex_pattern)}"
        else:
            gbnf_type = PydanticDataType.STRING.value

    elif isclass(field_type) and issubclass(field_type, float) and field_info and hasattr(field_info,
                                                                                          'json_schema_extra') and field_info.json_schema_extra is not None:
        # Retrieve precision attributes for floats
        max_precision = field_info.json_schema_extra.get('max_precision') if field_info and hasattr(field_info,
                                                                                                    'json_schema_extra') else None
        min_precision = field_info.json_schema_extra.get('min_precision') if field_info and hasattr(field_info,
                                                                                                    'json_schema_extra') else None
        max_digits = field_info.json_schema_extra.get('max_digit') if field_info and hasattr(field_info,
                                                                                             'json_schema_extra') else None
        min_digits = field_info.json_schema_extra.get('min_digit') if field_info and hasattr(field_info,
                                                                                             'json_schema_extra') else None

        # Generate GBNF rule for float with given attributes
        gbnf_type, rules = generate_gbnf_float_rules(max_digit=max_digits, min_digit=min_digits,
                                                     max_precision=max_precision,
                                                     min_precision=min_precision)

    elif isclass(field_type) and issubclass(field_type, int) and field_info and hasattr(field_info,
                                                                                        'json_schema_extra') and field_info.json_schema_extra is not None:
        # Retrieve digit attributes for integers
        max_digits = field_info.json_schema_extra.get('max_digit') if field_info and hasattr(field_info,
                                                                                             'json_schema_extra') else None
        min_digits = field_info.json_schema_extra.get('min_digit') if field_info and hasattr(field_info,
                                                                                             'json_schema_extra') else None

        # Generate GBNF rule for integer with given attributes
        gbnf_type, rules = generate_gbnf_integer_rules(max_digit=max_digits, min_digit=min_digits)

    else:
        gbnf_type, rules = gbnf_type, []

    if is_optional:
        gbnf_type += ")?"
        gbnf_type = "(" + gbnf_type

    if gbnf_type not in created_rules:
        return gbnf_type, rules
    else:
        if gbnf_type in created_rules:
            return gbnf_type, rules


def generate_gbnf_grammar(model: Type[BaseModel], processed_models: set, created_rules: dict) -> list:
    """

    Generate GBnF Grammar

    Generates a GBnF grammar for a given model.

    :param model: A Pydantic model class to generate the grammar for. Must be a subclass of BaseModel.
    :param processed_models: A set of already processed models to prevent infinite recursion.
    :param created_rules: A dict containing already created rules to prevent duplicates.
    :return: A list of GBnF grammar rules in string format.

    Example Usage:
    ```
    model = MyModel
    processed_models = set()
    created_rules = dict()

    gbnf_grammar = generate_gbnf_grammar(model, processed_models, created_rules)
    ```
    """
    if model in processed_models:
        return []

    processed_models.add(model)
    model_name = format_model_and_field_name(model.__name__)

    model_fields = {}

    if not issubclass(model, BaseModel):
        # For non-Pydantic classes, generate model_fields from __annotations__ or __init__
        if hasattr(model, '__annotations__') and model.__annotations__:
            model_fields = {name: (typ, ...) for name, typ in model.__annotations__.items()}
        else:
            init_signature = inspect.signature(model.__init__)
            parameters = init_signature.parameters
            model_fields = {name: (param.annotation, param.default) for name, param in parameters.items()
                            if name != 'self'}
    else:
        # For Pydantic models, use model_fields and check for ellipsis (required fields)
        model_fields = model.__annotations__

    model_rule_parts = []
    nested_rules = []

    for field_name, field_info in model_fields.items():
        if not issubclass(model, BaseModel):
            field_type, default_value = field_info
            # Check if the field is optional (not required)
            is_optional = (default_value is not inspect.Parameter.empty) and (default_value is not Ellipsis)
        else:
            field_type = field_info
            field_info = model.model_fields[field_name]
            is_optional = field_info.is_required is False and get_origin(field_type) is Optional
        rule_name, additional_rules = generate_gbnf_rule_for_type(model_name, format_model_and_field_name(field_name),
                                                                  field_type, is_optional,
                                                                  processed_models, created_rules, field_info)
        if rule_name not in created_rules:
            created_rules[rule_name] = additional_rules
        model_rule_parts.append(f'\"\\\"{field_name}\\\"\" ":" ws {rule_name}')  # Adding escaped quotes
        nested_rules.extend(additional_rules)

    fields_joined = ' ws ", " ws '.join(model_rule_parts)
    model_rule = f'{model_name} ::= "{{" ws {fields_joined} ws "}}"'
    all_rules = [model_rule] + nested_rules

    return all_rules


def generate_gbnf_grammar_from_pydantic(models: List[Type[BaseModel]], root_rule_class: str = None,
                                        root_rule_content: str = None) -> str:
    """
    Generate GBNF Grammar from Pydantic Models.

    This method takes a list of Pydantic models and uses them to generate a GBNF grammar string. The generated grammar string can be used for parsing and validating data using the generated
    * grammar.

    Parameters:
    - models (List[Type[BaseModel]]): A list of Pydantic models to generate the grammar from.
    - root_rule_class (str, optional): The name of the root model class. If provided, the generated grammar will have a root rule that matches the specified class. Default is None.
    - root_rule_content (str, optional): The content of the root model rule. This can be used to specify additional constraints or transformations for the root model. Default is None.

    Returns:
    - str: The generated GBNF grammar string.

    Examples:
        models = [UserModel, PostModel]
        grammar = generate_gbnf_grammar_from_pydantic(models)
        print(grammar)
        # Output:
        # root ::= UserModel | PostModel
        # ...
    """
    processed_models = set()
    all_rules = []
    created_rules = {}
    if root_rule_class is None:

        for model in models:
            model_rules = generate_gbnf_grammar(model, processed_models, created_rules)
            all_rules.extend(model_rules)

        root_rule = "root ::= " + " | ".join([format_model_and_field_name(model.__name__) for model in models])
        all_rules.insert(0, root_rule)
        return "\n".join(all_rules)
    elif root_rule_class is not None:
        root_rule = f"root ::= {format_model_and_field_name(root_rule_class)}\n"

        model_rule = fr'{format_model_and_field_name(root_rule_class)} ::= "{{" ws "\"{root_rule_class}\"" ":" ws grammar-models ws "}}"'
        fields_joined = " | ".join(
            [fr'{format_model_and_field_name(model.__name__)}-grammar-model' for model in models])

        grammar_model_rules = f'\ngrammar-models ::= {fields_joined}'
        mod_rules = []
        for model in models:
            mod_rule = fr'{format_model_and_field_name(model.__name__)}-grammar-model ::= '
            mod_rule += fr'"\"{format_model_and_field_name(model.__name__)}\"" "," "\"{root_rule_content}\"" ":"  {format_model_and_field_name(model.__name__)}' + '\n'
            mod_rules.append(mod_rule)
        grammar_model_rules += "\n" + "\n".join(mod_rules)
        for model in models:
            model_rules = generate_gbnf_grammar(model, processed_models, created_rules)
            all_rules.extend(model_rules)
        all_rules.insert(0, root_rule + model_rule + grammar_model_rules)
        return "\n".join(all_rules)


def get_primitive_grammar(grammar):
    type_list = []
    if "string-list" in grammar:
        type_list.append(str)
    if "boolean-list" in grammar:
        type_list.append(bool)
    if "integer-list" in grammar:
        type_list.append(int)
    if "float-list" in grammar:
        type_list.append(float)
    additional_grammar = [generate_list_rule(t) for t in type_list]
    primitive_grammar = r"""
boolean ::= "true" | "false"
string ::= "\"" ( ([^"\\'] | escaped-char)* ) "\""
escaped-char ::= "\\" ["\\/bfnrt"] | unicode-escape
unicode-escape ::= "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]
ws ::= " " | "\t" | "\n" | " " ws | "\t" ws | "\n" ws
fractional-part ::= [0-9]+
integer-part ::= [0-9]+
integer ::= [0-9]+"""
    return "\n" + '\n'.join(additional_grammar) + primitive_grammar


def generate_field_markdown(field_name: str, field_type: Type[Any], model: Type[BaseModel], depth=1) -> str:
    indent = '  ' * depth
    field_markdown = f"{indent}- **{field_name}** (`{field_type.__name__}`): "

    # Extracting field description from Pydantic Field using __model_fields__
    field_info = model.model_fields.get(field_name)
    field_description = field_info.description if field_info and field_info.description else "No description available."

    field_markdown += field_description + '\n'

    # Handling nested BaseModel fields
    if isclass(field_type) and issubclass(field_type, BaseModel):
        field_markdown += f"{indent}  - Details:\n"
        for name, type_ in field_type.__annotations__.items():
            field_markdown += generate_field_markdown(name, type_, field_type, depth + 2)

    return field_markdown


def generate_markdown_report(pydantic_models: List[Type[BaseModel]]) -> str:
    markdown = ""
    for model in pydantic_models:
        markdown += f"### {format_model_and_field_name(model.__name__)}\n"

        # Check if the model's docstring is different from BaseModel's docstring
        class_doc = getdoc(model)
        base_class_doc = getdoc(BaseModel)
        class_description = class_doc if class_doc and class_doc != base_class_doc else "No specific description available."

        markdown += f"{class_description}\n\n"
        markdown += "#### Fields\n"

        if isclass(model) and issubclass(model, BaseModel):
            for name, field_type in model.__annotations__.items():
                markdown += generate_field_markdown(format_model_and_field_name(name), field_type, model)
        markdown += "\n"

    return markdown


def format_json_example(example: dict, depth: int) -> str:
    indent = '    ' * depth
    formatted_example = '{\n'
    for key, value in example.items():
        value_text = f"'{value}'" if isinstance(value, str) else value
        formatted_example += f"{indent}{key}: {value_text},\n"
    formatted_example = formatted_example.rstrip(',\n') + '\n' + indent + '}'
    return formatted_example


def generate_text_documentation(pydantic_models: List[Type[BaseModel]], model_prefix="Model",
                                fields_prefix="Fields") -> str:
    documentation = ""
    for model in pydantic_models:
        documentation += f"{model_prefix}: {format_model_and_field_name(model.__name__)}\n"

        # Handling multi-line model description with proper indentation
        documentation += "  Description: "
        class_doc = getdoc(model)
        base_class_doc = getdoc(BaseModel)
        class_description = class_doc if class_doc and class_doc != base_class_doc else "No specific description available."
        documentation += "\n" + format_multiline_description(class_description, 2) + "\n\n"

        # Indenting the fields section
        documentation += f"  {fields_prefix}:\n"
        if isclass(model) and issubclass(model, BaseModel):
            for name, field_type in model.__annotations__.items():
                documentation += generate_field_text(name, field_type, model)
            documentation += "\n"

        if hasattr(model, 'Config') and hasattr(model.Config,
                                                'json_schema_extra') and 'example' in model.Config.json_schema_extra:
            documentation += f"  Expected Example Output for {format_model_and_field_name(model.__name__)}:\n"
            json_example = json.dumps(model.Config.json_schema_extra['example'])
            documentation += format_multiline_description(json_example, 2) + "\n"

    return documentation


def generate_field_text(field_name: str, field_type: Type[Any], model: Type[BaseModel], depth=1) -> str:
    indent = '    ' * depth
    field_text = f"{indent}{field_name} ({field_type.__name__}): \n"

    field_info = model.model_fields.get(field_name)
    field_description = field_info.description if field_info else "No description available."

    # Handling multi-line field description with proper indentation
    field_text += f"{indent}  Description: " + field_description + "\n"

    # Check for and include field-specific examples if available
    if hasattr(model, 'Config') and hasattr(model.Config,
                                            'json_schema_extra') and 'example' in model.Config.json_schema_extra:
        field_example = model.Config.json_schema_extra['example'].get(field_name)
        if field_example is not None:
            example_text = f"'{field_example}'" if isinstance(field_example, str) else field_example
            field_text += f"{indent}  Example: {example_text}\n"

    if isclass(field_type) and issubclass(field_type, BaseModel):
        field_text += f"{indent}  Details:\n"
        for name, type_ in field_type.__annotations__.items():
            field_text += generate_field_text(name, type_, field_type, depth + 2)

    return field_text


def format_multiline_description(description: str, indent_level: int) -> str:
    indent = '    ' * indent_level
    return indent + description.replace('\n', '\n' + indent)


def save_gbnf_grammar_and_documentation(grammar, documentation, grammar_file_path="./grammar.gbnf",
                                        documentation_file_path="./grammar_documentation.md"):
    try:
        with open(grammar_file_path, 'w') as file:
            file.write(grammar + get_primitive_grammar(grammar))
        print(f"Grammar successfully saved to {grammar_file_path}")
    except IOError as e:
        print(f"An error occurred while saving the grammar file: {e}")

    try:
        with open(documentation_file_path, 'w') as file:
            file.write(documentation)
        print(f"Documentation successfully saved to {documentation_file_path}")
    except IOError as e:
        print(f"An error occurred while saving the documentation file: {e}")


def remove_empty_lines(string):
    lines = string.splitlines()
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_no_empty_lines = "\n".join(non_empty_lines)
    return string_no_empty_lines


def generate_and_save_gbnf_grammar_and_documentation(pydantic_model_list, grammar_file_path="./generated_grammar.gbnf",
                                                     documentation_file_path="./generated_grammar_documentation.md",
                                                     root_rule_class: str = None, root_rule_content: str = None):
    documentation = generate_text_documentation(pydantic_model_list, "Output Model", "Output Fields")
    grammar = generate_gbnf_grammar_from_pydantic(pydantic_model_list, root_rule_class, root_rule_content)
    grammar = remove_empty_lines(grammar)
    print(grammar)
    save_gbnf_grammar_and_documentation(grammar, documentation, grammar_file_path, documentation_file_path)


class YourModel(BaseModel):
    float_field: float = Field(default=..., description="TEST", max_precision=2, min_precision=1)
    integer_field: int = Field(default=..., description="TEST", max_digit=5, min_digit=3)
    float_field2: float = Field(default=..., description="TEST", max_digit=5, min_digit=3, max_precision=2,
                                min_precision=1)
    integer_field2: int = Field(default=..., description="TEST", max_digit=5, min_digit=3)





