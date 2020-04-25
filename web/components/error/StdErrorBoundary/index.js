import React from "react";
import "./index.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true, error };
    }
    componentDidCatch(error, info) {
        // TODO: Log to a service
    }

    getErrorMessage = () => {
        return this.state.error.message;
    };

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return (
                <>
                    <div className="flex has-text-danger">
                        <FontAwesomeIcon icon="exclamation-triangle" />
                    </div>
                </>
            );
        }
        return this.props.children;
    }
}

/*

                    <div className="StdErrorReporter flex flex-gap">
                        <div>
                            <strong>An unknown error ocurred</strong>
                            <br />
                            {this.getErrorMessage()}
                        </div>
                        <div className="flex align-end v-center">
                            <div className="flex-grow">
                                <OutboundLink
                                    className="btn btn-secondary"
                                    to={getGhIssueUrl(
                                        this.state.error,
                                        this.props.tag
                                            ? this.props.tag
                                            : "error"
                                    )}
                                >
                                    Send bug report
                                </OutboundLink>
                            </div>
                        </div>
                    </div>
*/
