import React from "react";
import { StdErrorCollection } from "../../lib/utils/error";
import OutboundLink from "~/components/OutboundLink";
import { isDev } from "../../config";

// Test error display
/* const messageError = new StdErrorCollection("Something went wrong.");
const multipleErrors = new StdErrorCollection([
    "Many things went wrong",
    "Multiple things went wrong"
]);
const fieldErrors = new StdErrorCollection({
    password: "Wrong password input",
    bitches: "Many of them"
});
const jsError = new StdErrorCollection(new Error("Hai"));
*/

function renderError(error) {
    switch (error.type) {
        case "field":
            return (
                <>
                    <strong>
                        {error.fieldName.replace("project", "hashtag")}
                    </strong>
                    : {error.message}{" "}
                    {error.link !== null ? (
                        <OutboundLink to={error.link}>Read more</OutboundLink>
                    ) : (
                        ""
                    )}
                </>
            );

        case "unknown":
            return (
                <>
                    {error.message}
                    {isDev && (
                        <>
                            <br />
                            <pre>{error.stack}</pre>
                        </>
                    )}
                </>
            );
        default:
            return error.message;
    }
}

function renderMultipleErrors(error) {
    let res = [];
    error.errors.map(e => (res = [...res, renderError(e)]));
    return (
        <ul>
            {res.map(r => (
                <li>{r}</li>
            ))}
        </ul>
    );
}

const StdErrorMessages = ({ error = null }) => {
    if (error === null || !(error instanceof StdErrorCollection)) return null;

    if (error.getUnknownErrors().length) {
        return (
            <div className="alert is-danger">
                <div className="alert-body">
                    <b>An unknown error ocurred.</b>
                    {renderMultipleErrors(error)}
                    {!isDev && error.getUnknownErrors()[0].link !== null ? (
                        <>
                            <OutboundLink
                                className="btn btn-small btn-light"
                                to={error.getUnknownErrors()[0].link}
                            >
                                Report error
                            </OutboundLink>
                        </>
                    ) : null}
                </div>
            </div>
        );
    }

    return (
        <div className="alert is-danger">
            <div className="alert-body">
                <b>
                    {error.message} {error.code}
                </b>
                {error.errors.length > 1 && renderMultipleErrors(error)}
            </div>
        </div>
    );
};

export default StdErrorMessages;
