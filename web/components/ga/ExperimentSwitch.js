import React, { Component } from "react";
import { Experiment } from "~/vendor/ga";

export default class ExperimentSwitch extends Component {
    state = {
        active: false
    };

    componentDidMount() {
        new Experiment(this.props.experiment, () => {
            this.setState({ active: true });
        });
    }

    render() {
        if (this.state.active) {
            return this.props.variant;
        } else {
            return this.props.original;
        }
    }
}
