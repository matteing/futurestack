import isObject from "lodash/isObject";
import { isServer } from "~/config";
import flatten from "lodash/flatten";

class AxiosError extends Error {
  constructor(message, status_code = false, field_errors = null) {
    super(message);
    this.name = this.constructor.name;
    if (typeof Error.captureStackTrace === "function") {
      Error.captureStackTrace(this, this.constructor);
    } else {
      this.stack = new Error(message).stack;
    }

    this.status_code = status_code;
    this.field_errors = field_errors;
  }
}

function prettyAxiosError(error) {
  console.log(error.message);
  if (error.response) {
    if (error.response.data["non_field_errors"]) {
      throw new AxiosError(
        error.response.data["non_field_errors"],
        error.response.status
      );
    }
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    if (error.response.status === 500) {
      throw new AxiosError("A server error ocurred.", error.response.status);
    }

    if (error.response.status === 404) {
      throw new AxiosError("Not found.", error.response.status);
    }

    if (
      error.response.status === 400 &&
      Object.keys(error.response.data).length > 0
    ) {
      throw new AxiosError(
        "Please fill or correct the following fields to continue.",
        error.response.status,
        error.response.data
      );
    }

    throw new AxiosError(
      "An error occurred sending this request. Try again later.",
      error.response.status
    );
  } else if (error.request) {
    // The request was made but no response was received
    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
    // http.ClientRequest in node.js
    if (!navigator.onLine) {
      throw new Error("No internet connection found. Try again later.");
    } else if (error.message.includes("413")) {
      throw new AxiosError("This file is too large!");
    } else {
      throw new Error(
        "Oh no! Makerlog seems to be down. Please try again later."
      );
    }
  } else {
    // Something happened in setting up the request that triggered an Error
    throw new Error("Unknown error. Try again later.");
  }
}

function errorArray(obj) {
  if (!!obj && obj.constructor === Array) {
    return obj;
  } else {
    return [obj];
  }
}

export async function axiosWrapper(fn, ...args) {
  try {
    return await fn(...args);
  } catch (e) {
    console.log(`Makerlog: ${e.message}`);
    prettyAxiosError(e);
  }
}

export function errorStruct(
  type,
  message,
  code = 0,
  fieldName = null,
  link = null,
  stack = null
) {
  return {
    type,
    message,
    code,
    fieldName,
    link,
    stack,
  };
}

export function error(e) {
  console.log("Error!", e);
  let errors = [];
  if (typeof e === "string") {
    errors.push(errorStruct("message", e, 0, null, null));
  } else if (Array.isArray(e)) {
    errors = e.map((err) => error(err));
  } else if (e instanceof AxiosError) {
    if (e.field_errors === null) {
      errors.push(
        errorStruct(
          "message",
          e.message,
          e.status_code ? e.status_code : 0,
          null,
          null,
          null
        )
      );
    } else {
      errors = [...error(e.field_errors)];
    }
  } else if (e instanceof StdError) {
    errors = [e.toStruct()];
  } else if (
    isObject(e) &&
    !(e instanceof Error) &&
    !(e instanceof ValidationError)
  ) {
    for (const [key, value] of Object.entries(e)) {
      errors.push(errorStruct("field", value, 0, key, null));
    }
  } else if (e instanceof ValidationError) {
    if (e.fieldName) {
      errors.push(
        errorStruct(
          "field",
          e.message,
          e.status_code ? e.status_code : 0,
          e.fieldName,
          null,
          null
        )
      );
    } else {
      errors.push(
        errorStruct(
          "message",
          e.message,
          e.status_code ? e.status_code : 0,
          null,
          null,
          null
        )
      );
    }
  } else if (e instanceof Error) {
    errors.push(
      errorStruct(
        "unknown",
        e.message,
        -1,
        null,
        getGhIssueUrl(e),
        e.stack ? e.stack : null
      )
    );
  }

  return flatten(errors);
}

export function getFirstErrorString(eStruct) {
  if (!eStruct.length) return "No errors occurred.";
  if (eStruct.length === 1) {
    return eStruct[0].message;
  } else {
    return "Multiple errors ocurred.";
  }
}

export function getErrorCodeString(eStruct) {
  return `(${eStruct.map((e) => e.code).join(", ")})`;
}

export const getGhIssueUrl = (error, tag = "error-ocurred") => {
  if (isServer) return "https://github.com/matteing/makerlog/issues/new";
  let data = {
    body: `User: <your username here>\nUA=${
      window.navigator.userAgent
    }\nTag=${tag}\nLanguage=${window.navigator.language}\n${error.toString()}`,
    labels: ["bug"],
  };
  const params = new URLSearchParams(data);
  return `https://github.com/matteing/makerlog/issues/new?${params.toString()}`;
};

export class StdErrorCollection {
  constructor(e) {
    this.errors = error(e);
    this.message = this.message();
    this.code = this.code();
  }

  message = () => {
    return getFirstErrorString(this.errors);
  };

  code = () => {
    return getErrorCodeString(this.errors);
  };

  getFieldErrors = () => {
    return this.errors.filter((e) => e.type === "field");
  };

  getMessageErrors = () => {
    return this.errors.filter((e) => e.type === "message");
  };

  getUnknownErrors = () => {
    return this.errors.filter((e) => e.type === "unknown");
  };
}

export class StdError {
  constructor(e) {
    this.errors = error(e);
    this.message = this.message();
  }
}

export class ValidationError {
  constructor(message, fieldName = null) {
    this.message = message;
    this.fieldName = fieldName;
  }
}

export function renderHelpOrError(help = null, name, e) {
  if (
    e !== null &&
    name &&
    e instanceof StdErrorCollection &&
    e.getFieldErrors().find((e) => e.fieldName === name)
  ) {
    const err = e.getFieldErrors().find((r) => r.fieldName === name);
    return <p className="help has-text-danger">{err.message}</p>;
  }

  return help ? <p className="help">{help}</p> : null;
}

export { prettyAxiosError, errorArray };
