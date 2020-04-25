import React from "react";
import PropTypes from "prop-types";
import { Track } from "../vendor/ga";

const OutboundLink = ({
    to,
    href,
    children,
    className = null,
    style = null
}) => (
    <a
        href={to || href}
        target={"_blank"}
        rel="noopener noreferrer"
        className={className}
        style={style}
        onClick={() => {
            new Track().outbound(to || href);
        }}
    >
        {children}
    </a>
);

OutboundLink.propTypes = {
    to: PropTypes.string
};

export default OutboundLink;
