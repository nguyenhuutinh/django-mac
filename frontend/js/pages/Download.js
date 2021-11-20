import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import { useDispatch, useSelector } from 'react-redux';

import DjangoImgSrc from '../../assets/images/django-logo-negative.png';
import { creators } from '../store/rest_check';

const Download = (props) => {
  const dispatch = useDispatch();
  const restCheck = useSelector((state) => state.restCheck);
  const [loading, showLoading] = useState(false);

  useEffect(() => {
    var {location} = props
    var file_slug = location.pathname.replaceAll("/download/","")
    showLoading(true)
    const action = creators.fetchRestCheck(file_slug);
    dispatch(action);
  }, [dispatch]);



  useEffect(() => {

    console.log(path)
    return () => {

    }
  }, [])
  return (
    <div>
      <h3>Download</h3>
      <div id="django-logo-wrapper">
      <img alt="Django Negative Logo" src={DjangoImgSrc} />

      </div>
      <div>{restCheck.result  ? restCheck.result : "loading ..." }</div>
      {/* <Button variant="outline-dark" onClick={() => setShowBugComponent(true)}>
        Click to test if Sentry is capturing frontend errors! (Should only work in Production)
      </Button>
      {showBugComponent && showBugComponent.field.notexist} */}

    </div>
  );
}

export default Download;
