import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import {
  Box, Typography, Grid, Paper, Table, TableHead, TableBody, TableRow, TableCell
} from '@material-ui/core';

const styles = theme => ({
  root: {
    display: 'flex',
    flexGrow: 1,
    margin: theme.spacing(1),
  },
  content: {
    padding: theme.spacing(2),
    width: '100%',
    height: '100%',
  },
});

class Report extends React.Component {
  constructor(props) {
    super(props);
    this.state = {

    };
  }

  render() {
    const { classes } = this.props;
    return (
      <Grid
        container
        className={classes.root}
      >
        <Paper className={classes.content}>
          <Grid
            container
            spacing={2}
            direction="row"
            justify="space-evenly"
            alignItems="center"
          >
            <Grid item xs={4}>
              <Paper className={classes.content}>
                asdfasfas
              </Paper>
            </Grid>
            <Grid item xs={7}>

              <Typography variant="h5" gutterBottom noWrap>Overall</Typography>
              <Typography variant="h6" noWrap>
                {`Accuracy: ${this.props.data['accuracy'].toFixed(4)}`}
              </Typography>
              <Table className={classes.table}>
                <TableHead>
                  <TableRow>
                    <TableCell>Method</TableCell>
                    <TableCell align="right">F1-Score</TableCell>
                    <TableCell align="right">Precision</TableCell>
                    <TableCell align="right">Recall</TableCell>
                    <TableCell align="right">Support</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow key={'macro_avg'}>
                    <TableCell component="th" scope="row">Macro Average</TableCell>
                    <TableCell align="right">{this.props.data['macro_avg']['precision'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['macro_avg']['recall'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['macro_avg']['f1_score'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['macro_avg']['support'].toFixed(4)}</TableCell>
                  </TableRow>
                  <TableRow key={'weighted_avg'}>
                    <TableCell component="th" scope="row">Weighted Average</TableCell>
                    <TableCell align="right">{this.props.data['weighted_avg']['precision'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['weighted_avg']['recall'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['weighted_avg']['f1_score'].toFixed(4)}</TableCell>
                    <TableCell align="right">{this.props.data['weighted_avg']['support'].toFixed(4)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>

              <Box mt="2em" />
              <Typography variant="h5" gutterBottom noWrap>By Class</Typography>
              <Table className={classes.table}>
                <TableHead>
                  <TableRow>
                    <TableCell>Class</TableCell>
                    <TableCell align="right">F1-Score</TableCell>
                    <TableCell align="right">Precision</TableCell>
                    <TableCell align="right">Recall</TableCell>
                    <TableCell align="right">Support</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>

                  {this.props.data['by_class'].map(row => (
                    <TableRow key={row['class_name']}>
                      <TableCell component="th" scope="row">
                        {row['class_name']}
                      </TableCell>
                      <TableCell align="right">{row['precision'].toFixed(4)}</TableCell>
                      <TableCell align="right">{row['recall'].toFixed(4)}</TableCell>
                      <TableCell align="right">{row['f1_score'].toFixed(4)}</TableCell>
                      <TableCell align="right">{row['support'].toFixed(4)}</TableCell>
                    </TableRow>
                  ))}

                </TableBody>
              </Table>

            </Grid>
          </Grid>
        </Paper>
      </Grid>
    );
  }
}

Report.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Report);