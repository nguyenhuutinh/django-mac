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

    // console.log(path)
    return () => {

    }
  }, [])
  return (
    <div class="main-screen">
      <h3>Download System v5</h3>
      <div >
      {/* <img alt="Django Negative Logo" src={DjangoImgSrc} /> */}

      <br/>
      </div>
      <div>{restCheck.result  ? restCheck.result : "checking file ..." }</div>
      <br/>
      <br/>
      <br/>
      {restCheck.result && <Button style={{ width: "200px"}} variant="outline-success" onClick={() => window.location = restCheck.result }>
        Download File
      </Button>}


    </div>
  );
}

export default Download;
