import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import {
  InputLabel, MenuItem, FormHelperText, FormControl, Select, Typography
} from '@material-ui/core';

const styles = theme => ({
  root: {
    display: 'flex',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  toolbar: theme.mixins.toolbar,
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
});

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      dimReduce: "",
      classifier: ""
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.sessionId !== prevProps.sessionId) {
      this.fetchSessionData();
    }
  }

  fetchSessionData = () => {
    axios.get(`http://localhost:5000/api/sessions/${this.props.sessionId}`)
      .then(res => {
        const session = res.data;
        console.log(session);
      });
  }

  handleDimReduceChange = event => {
    this.setState({ dimReduce: event.target.value });
  }

  handleClassifierChange = event => {
    this.setState({ classifier: event.target.value });
  }

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.root} autoComplete="off">
        <CssBaseline />
        <main className={classes.content}>
          <div className={classes.toolbar} />

          <Typography variant="h4" gutterBottom>
            {`Session #${this.props.sessionId}`}
          </Typography>

          <FormControl className={classes.formControl}>
            <InputLabel shrink htmlFor="dim-reduce-label-placeholder">
              <Typography variant="h4" noWrap>Dimensionality Reduction</Typography>
            </InputLabel>
            <Select
              value={this.state.dimReduce}
              onChange={this.handleDimReduceChange}
              inputProps={{
                name: 'dim-reduce',
                id: 'dim-reduce-label-placeholder'
              }}
              displayEmpty
              name="dim-reduce"
              className={classes.selectEmpty}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              <MenuItem value={"pca"}>PCA</MenuItem>
              <MenuItem value={"nmf"}>NMF</MenuItem>
              <MenuItem value={"chi2"}>Chi-square</MenuItem>
            </Select>
            <FormHelperText>Select dimensionality reduction/feature selection method</FormHelperText>
          </FormControl>

          <FormControl className={classes.formControl}>
            <InputLabel shrink htmlFor="classifier-label-placeholder">
              <Typography variant="h4" noWrap>Classifier</Typography>
            </InputLabel>
            <Select
              value={this.state.classifier}
              onChange={this.handleClassifierChange}
              inputProps={{
                name: 'classifier',
                id: 'classifier-label-placeholder'
              }}
              displayEmpty
              name="classifier"
              className={classes.selectEmpty}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              <MenuItem value={"random_forest"}>Random Forest</MenuItem>
              <MenuItem value={"ada_boost"}>ADA Boost</MenuItem>
              <MenuItem value={"naive_bayes"}>Naive Bayes</MenuItem>
            </Select>
            <FormHelperText>Select classifier model</FormHelperText>
          </FormControl>
        </main>
      </div >
    );
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Dashboard);