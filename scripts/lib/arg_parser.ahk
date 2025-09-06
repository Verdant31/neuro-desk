#Requires AutoHotkey v2.0

; Utility function to parse named arguments
; Supports: strings, numbers, and arrays (JSON format)
; Example:
; args := ParseArgs(paramConfig)
; param := GetParam(args, "paramName", defaultValue)
; hasParam := HasParam(args, "paramName")
ParseArgs(paramConfig := "") {
    args := Map()

    for i, arg in A_Args {
        if (SubStr(arg, 1, 2) = "--") {
            param := SubStr(arg, 3)

            if (i < A_Args.Length && SubStr(A_Args[i + 1], 1, 2) != "--") {
                value := A_Args[i + 1]
                if (IsNumber(value)) {
                    args[param] := Number(value)
                }
                else if (SubStr(value, 1, 1) = "[" && SubStr(value, -1) = "]") {
                    try {
                        arrayStr := SubStr(value, 2, StrLen(value) - 2)
                        arrayItems := StrSplit(arrayStr, ",")
                        parsedArray := []

                        for j, item in arrayItems {
                            item := Trim(item)
                            if (SubStr(item, 1, 1) = "'" && SubStr(item, -1) = "'") {
                                item := SubStr(item, 2, StrLen(item) - 2)
                            } else if (SubStr(item, 1, 1) = '"' && SubStr(item, -1) = '"') {
                                item := SubStr(item, 2, StrLen(item) - 2)
                            }
                            if (IsNumber(item)) {
                                parsedArray.Push(Number(item))
                            } else {
                                parsedArray.Push(item)
                            }
                        }
                        args[param] := parsedArray
                    } catch {
                        args[param] := value
                    }
                }
                else {
                    args[param] := value
                }
            }
        }
    }

    if (paramConfig != "") {
        ValidateArgs(args, paramConfig)
    }

    return args
}

ValidateArgs(args, paramConfig) {
    if (!paramConfig.Has("required") && !paramConfig.Has("optional")) {
        throw Error("Invalid parameter configuration: must have 'required' and/or 'optional' keys")
    }

    required := paramConfig.Has("required") ? paramConfig["required"] : []
    optional := paramConfig.Has("optional") ? paramConfig["optional"] : []
    validation := paramConfig.Has("validation") ? paramConfig["validation"] : Map()

    missingParams := []
    for param in required {
        if (!args.Has(param) || args[param] = "") {
            missingParams.Push(param)
        }
    }

    if (missingParams.Length > 0) {
        errorMsg := "Missing required parameters: " . Join(missingParams, ", ")
        throw Error(errorMsg)
    }

    for param, value in args {
        if (validation.Has(param)) {
            paramValidation := validation[param]

            if (paramValidation.Has("type")) {
                if (paramValidation["type"] = "number" && !IsNumber(value)) {
                    throw Error("Parameter '" . param . "' must be a number, got: " . value)
                }
                if (paramValidation["type"] = "string" && IsNumber(value)) {
                    throw Error("Parameter '" . param . "' must be a string, got: " . value)
                }
            }

            if (paramValidation.Has("valid_values")) {
                validFound := false
                for validValue in paramValidation["valid_values"] {
                    if (value = validValue) {
                        validFound := true
                        break
                    }
                }
                if (!validFound) {
                    throw Error("Parameter '" . param . "' must be one of: " . Join(paramValidation["valid_values"],
                        ", ") . ". Got: " . value)
                }
            }

            if (paramValidation.Has("min") && IsNumber(value)) {
                if (value < paramValidation["min"]) {
                    throw Error("Parameter '" . param . "' must be >= " . paramValidation["min"] . ", got: " . value)
                }
            }
            if (paramValidation.Has("max") && IsNumber(value)) {
                if (value > paramValidation["max"]) {
                    throw Error("Parameter '" . param . "' must be <= " . paramValidation["max"] . ", got: " . value)
                }
            }
        }
    }
}

Join(arr, delimiter) {
    result := ""
    for i, item in arr {
        if (i > 1) {
            result .= delimiter
        }
        result .= item
    }
    return result
}

GetParam(args, paramName, defaultValue := "") {
    return args.Has(paramName) ? args[paramName] : defaultValue
}

HasParam(args, paramName) {
    return args.Has(paramName)
}
