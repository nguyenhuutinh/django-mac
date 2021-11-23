import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import { useDispatch, useSelector } from 'react-redux';

import DjangoImgSrc from '../../assets/images/django-logo-negative.png';
import { creators } from '../store/rest_check';

const Fshare = (props) => {
  const dispatch = useDispatch();
  const fshareCheck = useSelector((state) => state.fshareCheck);
  const [loading, showLoading] = useState(false);
  const [code, setCode] = useState();




  useEffect(() => {

    showLoading(false)
    return () => {

    }
  }, [fshareCheck])

  const handleChange = (event) => {
    setCode(event.target.value);
  }
  const handleSubmit = (e) =>{
    e.preventDefault();
    var {location} = props
    showLoading(true)
    const action = creators.getFshareLink(code);
    dispatch(action);
  }
  return (
    <div class="main-screen">
      <h3>Fshare Vip Download v5</h3>
      <div >
      <form onSubmit={(e)=>{handleSubmit(e)}}>
        <label>
          Name:
          <input type="text" value={code} onChange={(e)=>handleChange(e)} />
        </label>
        <input type="submit" value="Submit" />
      </form>

      <br/>
      </div>
      <div>{loading &&  "checking file ..." }</div>
      <br/>
      <br/>
      <br/>
      {fshareCheck.result && typeof fshareCheck.result === 'string' && fshareCheck.result.startsWith("https") && <Button style={{ width: "400px"}} variant="outline-success" onClick={() => window.location = fshareCheck.result }>
        File is Ready. Click Here to Download
      </Button>}
      {fshareCheck.result && typeof fshareCheck.result === JSON && <div>{JSON.stringify(fshareCheck.result) }</div>}
      {fshareCheck.result && typeof fshareCheck.result === String && <div>{(fshareCheck.result) }</div>}
    </div>
  );
}

export default Fshare;