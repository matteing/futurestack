import PropTypes from "prop-types";
import React from "react";
import { StdErrorCollection } from "../../lib/utils/error";
import StdErrorMessages from "~/components/forms/StdErrorMessages";

const renderFieldErrors = fieldErrors => {
    if (fieldErrors !== null && fieldErrors.constructor === Array) {
        let list = [];
        fieldErrors.map(o => {
            Object.keys(o).map(k => {
                list.push(
                    <li>
                        {k === "non_field_errors" ? null : <b>{k}:</b>} {o[k]}
                    </li>
                );

                return true;
            });

            return true;
        });

        return <ul>{list}</ul>;
    }

    if (fieldErrors !== null && typeof fieldErrors === "object") {
        let list = [];
        Object.keys(fieldErrors).map(k => {
            list.push(
                <li>
                    <b>{k}</b>: {fieldErrors[k].join(", ")}
                </li>
            );

            return true;
        });

        return <ul>{list}</ul>;
    }

    if (typeof fieldErrors === "string") return fieldErrors;

    return null;
};

const ErrorMessageList = ({
    errorMessages,
    fieldErrors,
    errors = null,
    nonFieldOnly = false
}) => {
    if (errors !== null && typeof errors === "object" && nonFieldOnly)
        return null;

    if (
        errors instanceof StdErrorCollection ||
        errorMessages instanceof StdErrorCollection ||
        fieldErrors instanceof StdErrorCollection
    ) {
        return (
            <StdErrorMessages errors={errors || errorMessages || fieldErrors} />
        );
    }

    return errorMessages || fieldErrors || errors ? (
        <div className="alert is-danger" danger>
            <div className="alert-body">
                <ul className="unstyled">
                    <b>
                        {errorMessages &&
                            errorMessages.map(message => (
                                <li key={message}>{message}</li>
                            ))}
                    </b>
                    {errorMessages && fieldErrors && <hr />}
                    {(errors || fieldErrors) && (
                        <div>{renderFieldErrors(errors || fieldErrors)}</div>
                    )}
                </ul>
            </div>
        </div>
    ) : null;
};

ErrorMessageList.propTypes = {
    errorMessages: PropTypes.array.isRequired
};

export default ErrorMessageList;
