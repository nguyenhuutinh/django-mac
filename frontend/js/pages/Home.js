import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import { useDispatch, useSelector } from 'react-redux';

import DjangoImgSrc from '../../assets/images/django-logo-negative.png';
import { creators } from '../store/rest_check';

const Home = () => {
  const dispatch = useDispatch();
  const restCheck = useSelector((state) => state.restCheck);
  const [loading, showLoading] = useState(false);

  useEffect(() => {
    showLoading(true)
    const action = creators.fetchRestCheck();
    dispatch(action);
  }, [dispatch]);

  const [showBugComponent, setShowBugComponent] = useState(false);

  return (
    <>
      <div>
        <h3>Hello World</h3>
        </div>

    </>
  );
};

export default Home;
