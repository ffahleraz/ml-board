import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { withStyles, createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import {
  Drawer, AppBar, Toolbar, List, Divider, Typography, ListItem,
  ListItemText, Button, Icon
} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';

import Dashboard from './Dashboard'

const theme = createMuiTheme({
  palette: {
    type: 'dark',
  }
});

const drawerWidth = 300;

const styles = theme => ({
  root: {
    display: 'flex',
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  addButton: {
    margin: theme.spacing(1),
  },
  toolbar: theme.mixins.toolbar,
});

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sessions: [],
      currSessionId: ""
    };
  }

  componentDidMount() {
    this.fetchSessions();
  }

  fetchSessions = () => {
    axios.get(`http://localhost:5000/api/sessions`)
      .then(res => {
        const sessions = res.data.sessions;
        this.setState({ sessions });
      });
  }

  handleItemListClick = sessionId => {
    this.setState({ currSessionId: sessionId });
  }

  handleAddButtonClick = () => {
    axios.post(`http://localhost:5000/api/create`, {})
      .then(res => {
        const newSessionId = res.data.id;
        this.setState({ currSessionId: newSessionId });
        this.fetchSessions();
      });
  }

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.root}>
        <MuiThemeProvider theme={theme}>
          <CssBaseline />
          <AppBar position="fixed" color="default" className={classes.appBar}>
            <Toolbar>
              <Typography variant="h4" noWrap>
                ML-Board
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer
            className={classes.drawer}
            variant="permanent"
            classes={{
              paper: classes.drawerPaper,
            }}
          >
            <div className={classes.toolbar} />
            <Button
              variant="contained"
              size="large"
              color="primary"
              className={classes.addButton}
              onClick={this.handleAddButtonClick}
            >
              <AddIcon />
              New Session
            </Button>
            <Divider />
            <List>
              {this.state.sessions.map(session => (
                <ListItem button key={session["id"]} onClick={() => { this.handleItemListClick(session["id"]) }} >
                  <ListItemText
                    primary={`Session ${session["id"]}`}
                    secondary={`Created at ${session["created_at"]}`}
                  />
                </ListItem>
              ))}
            </List>
          </Drawer>
          {this.state.currSessionId !== "" && (
            <Dashboard sessionId={this.state.currSessionId} />
          )}
        </MuiThemeProvider>
      </div>
    );
  }
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(App);