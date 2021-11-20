import React, { useEffect } from 'react';
import { hot } from 'react-hot-loader/root';
import { Provider } from 'react-redux';

import Home from './pages/Home';
import Download from './pages/Download.js';
import configureStore from './store';
import SentryBoundary from './utils/SentryBoundary';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

const store = configureStore({});
const App = (props) => (

  <SentryBoundary>
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>

          </Route>
            <Route path="/download/:topicId" element={ <Download  name="Sara" location={window.location}/>}>

          </Route>
        </Routes>
      </BrowserRouter>
    </Provider>
  </SentryBoundary>
);

export default hot(App);
