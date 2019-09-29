import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { withStyles } from '@material-ui/core/styles';
import {
  Grid, Paper, Box, MenuItem, Select, Typography, Button
} from '@material-ui/core';

import Report from './Report'

const styles = theme => ({
  root: {
    display: 'flex',
    flexGrow: 1,
    marginTop: theme.spacing(8),
    padding: theme.spacing(2),
  },
  content: {
    padding: theme.spacing(2),
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  button: {
    margin: theme.spacing(1),
  },
});

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      status: 0,
      createdAt: "",
      dimReduction: "",
      classifier: "",
      dataFilename: "",
      report: null
    };
  }

  componentDidMount() {
    this.fetchSessionData();
  }

  componentDidUpdate(prevProps) {
    if (this.props.sessionId !== prevProps.sessionId) {
      this.fetchSessionData();
    }
  }

  fetchSessionData = () => {
    axios.get(`http://localhost:5000/api/sessions/${this.props.sessionId}`)
      .then(res => {
        this.setState({
          status: res.data['status'],
          createdAt: res.data['created_at'],
          dimReduction: res.data['dim_reduction'],
          classifier: res.data['classifier'],
          dataFilename: res.data['data_filename'],
          report: res.data['report'],
        });
      })
      .catch(err => {
        alert(err);
      });
  }

  trainSession = () => {
    const url = `http://localhost:5000/api/train`;

    const formData = new FormData();
    formData.append('data', this.state.data);
    const params = JSON.stringify({
      'session_id': this.props.sessionId,
      'dim_reduction': this.state.dimReduction,
      'classifier': this.state.classifier
    });
    formData.append('params', params);
    const config = {
      headers: {
        'content-type': 'multipart/form-data'
      }
    };

    axios.post(url, formData, config)
      .then(res => {
        console.log(res);
        this.setState({ report: res.data.report });
      })
      .catch(err => {
        if (err.response) {
          alert(err.response.data);
        } else {
          alert(err);
        }
      });
  }

  handleDimReductionChange = event => {
    this.setState({ dimReduction: event.target.value, report: null });
  }

  handleClassifierChange = event => {
    this.setState({ classifier: event.target.value, report: null });
  }

  handleTrainButtonClick = () => {
    this.trainSession();
  }

  handleDataUploadChange = event => {
    this.setState({
      data: event.target.files[0], dataFilename: event.target.files[0].name,
      report: null,
    });
  }

  render() {
    const { classes } = this.props;
    return (
      <Grid
        container
        spacing={2}
        className={classes.root}
      >
        <Grid item xs={12}>
          <Paper className={classes.content}>
            <Typography variant="h4" gutterBottom>
              <Box fontWeight="fontWeightBold">
                {`Session #${this.props.sessionId}`}
              </Box>
            </Typography>
            <Typography variant="subtitle1">
              {`Created at ${this.state.createdAt}`}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={6}>
          <Paper className={classes.content}>
            <Typography variant="h5">
              Dimensionality Reduction
            </Typography>
            <Select
              value={this.state.dimReduction}
              onChange={this.handleDimReductionChange}
              inputProps={{
                name: 'dim-reduce',
                id: 'dim-reduce-label-placeholder'
              }}
              displayEmpty
              name="dim-reduce"
              fullWidth
              className={classes.selectEmpty}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              <MenuItem value={"pca"}>PCA</MenuItem>
              <MenuItem value={"nmf"}>NMF</MenuItem>
              <MenuItem value={"chi2"}>Chi-square</MenuItem>
            </Select>
          </Paper>
        </Grid>

        <Grid item xs={6}>
          <Paper className={classes.content}>
            <Typography variant="h5">
              Classifier Model
            </Typography>
            <Select
              value={this.state.classifier}
              onChange={this.handleClassifierChange}
              inputProps={{
                name: 'classifier',
                id: 'classifier-label-placeholder'
              }}
              displayEmpty
              name="classifier"
              fullWidth
              className={classes.selectEmpty}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              <MenuItem value={"random_forest"}>Random Forest</MenuItem>
              <MenuItem value={"ada_boost"}>ADA Boost</MenuItem>
              <MenuItem value={"naive_bayes"}>Naive Bayes</MenuItem>
            </Select>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper className={classes.content}>
            <Typography variant="h5" gutterBottom>
              Dataset
            </Typography>

            <Grid
              container
              direction="row"
              justify="space-evenly"
              alignItems="center"
            >
              <Grid item xs={2}>
                <Typography variant="h6" noWrap>
                  {this.state.dataFilename ? (
                    <Box fontFamily="Monospace">{this.state.dataFilename}</Box>
                  ) : (
                      <Box fontFamily="Monospace" fontStyle="italic" color="orange">
                        not selected
                      </Box>
                    )}
                </Typography>
              </Grid>

              <Grid item xs={8}>
                <Button
                  variant="contained"
                  component="label"
                  fullWidth
                  className={classes.button}
                >
                  {this.state.dataFilename ? 'Change' : 'Upload'}
                  <input
                    type="file"
                    onChange={this.handleDataUploadChange}
                    style={{ display: 'none' }}
                  />
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper className={classes.content}>
            <Button
              variant="contained"
              size="large"
              color="secondary"
              fullWidth
              className={classes.button}
              onClick={this.handleTrainButtonClick}
              disabled={!this.state.dimReduction || !this.state.classifier || (!this.state.data && !this.state.status)}
            >
              Train
            </Button>
          </Paper>
        </Grid>
        {this.state.report && <Report data={this.state.report} />}
      </Grid>
    );
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Dashboard);