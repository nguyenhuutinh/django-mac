import React, { useEffect } from 'react';
import { hot } from 'react-hot-loader/root';
import { Provider } from 'react-redux';

import Home from './pages/Home';
import Download from './pages/Download.js';
import Fshare from './pages/Fshare.js';
import Ads from './pages/Ads.js';
import configureStore from './store';
import SentryBoundary from './utils/SentryBoundary';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

const store = configureStore({});
const App = (props) => (
  <SentryBoundary>
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}></Route>
          <Route
            path="/drive/:topicId"
            element={<Download location={window.location} />}
          ></Route>
          <Route path="/fshare" element={<Fshare  location={window.location} />}></Route>
          <Route path="/ads" element={<Ads  location={window.location} />}></Route>
        </Routes>
      </BrowserRouter>
    </Provider>
  </SentryBoundary>
);

export default hot(App);
