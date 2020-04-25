import React, { Component } from "react";

export default class ExperimentContainer extends Component {
    state = {
        active: false
    };

    componentDidMount() {
        new Experiment(this.props.experiment, () => {
            this.setState({ active: true });
        });
    }

    render() {
        const Component = this.props.children;
        return (
            <Component
                experiment={this.props.experiment}
                experimentActive={this.props.active}
            />
        );
    }
}
