import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {Form, Button, ButtonGroup, FormControl} from 'react-bootstrap';
import DjangoImgSrc from '../../assets/images/django-logo-negative.png';
import { creators } from '../store/rest_check';
import qs from 'qs';
const Ads = (props) => {
  const dispatch = useDispatch();
  const fshareCheck = useSelector((state) => state.fshareCheck);
  const [loading, showLoading] = useState(false);
  const [code, setCode] = useState();
  const [password, setPass] = useState();
  const [server, setServer] = useState(1);

  useEffect(() => {
    const action = creators.postShorten("https://download.cmacdrive.com/drive/microsoft-office-365-2019-v16-53");
    dispatch(action);
    return () => {

    }
  }, [])

  useEffect(() => {

    showLoading(false)
    return () => {

    }
  }, [fshareCheck])

  const handleChange = (event) => {
    setCode(event.target.value);
  }
  const handlePassChange = (event) => {
    setPass(event.target.value);
  }
  const getParameterByName = (name, url = window.location.href) =>{
    let searchParams = new URLSearchParams(url);
    for (let p of searchParams) {
      console.log(p);
    }
    console.log(url, searchParams.toString())
    return searchParams.get(name)

}
  const handleSubmit = (e) =>{
    e.preventDefault();
    console.log(e)
    showLoading(true)
    // console.log(code)
    var newCode = code
    let token = ""
    if(code.startsWith("https")){
      let url = new URL(code);

      // Delete the foo parameter.
      // if(url.search.has('token')){
      //   token = url.get("token")
      // }
      token = getParameterByName("token", url.search)
      console.log("token", token)

      url.hash = ""
      url.search = ""
      console.log(url.toString())
      newCode  = url.toString().replaceAll("https://www.fshare.vn/file/","")


      newCode  = newCode.replaceAll("https://fshare.vn/file/","")
      newCode  = newCode.replaceAll("fshare.vn/file/","")
      console.log("replace",newCode)
    }
    if(code.startsWith("www.fshare.vn/file/")){
      newCode  = newCode.replaceAll("www.fshare.vn/file/","")
    }
    if(code.startsWith("fshare.vn")){
      newCode  = newCode.replaceAll("fshare.vn/file/","")
    }
    // console.log(newCode)
    const action = creators.getFshareLink(newCode, server, password, token);
    dispatch(action);
  }
  console.log("fshareCheck", fshareCheck.result, typeof fshareCheck.result === 'json')
  return (
    <div class="main-screen">
      <h3>Fshare Vip Download v5</h3>

      <div >
      <Form onSubmit={(e)=>{handleSubmit(e)}} >
       <Form.Group className="mb-3" controlId="formBasicServer">
          <Form.Label> Server {server}</Form.Label>
          <ButtonGroup aria-label="Server">
            <Button variant={server == 1 ? "primary" : "secondary"} style={{marginRight: "10px"}} onClick={()=>setServer(1)}>1</Button>
            {/* <Button variant={server == 2 ? "primary" : "secondary"} style={{marginRight: "10px"}}  onClick={()=>setServer(2)}>2</Button> */}
            {/* <Button variant={server == 3 ? "primary" : "secondary"} style={{marginRight: "10px"}}  onClick={()=>setServer(3)}>3</Button> */}
          </ButtonGroup>
        </Form.Group>

        <Form.Group className="mb-3" controlId="formBasicCode">
          <Form.Label>Fshare Link or Code:</Form.Label>

          <FormControl type="text" value={code} onChange={(e)=>handleChange(e)} />
          <Form.Label>File Password:</Form.Label>

          <FormControl type="text" value={password} onChange={(e)=>handlePassChange(e)} />
        </Form.Group>
        <Button type="submit" value="Submit" disabled={loading} loading={loading}>{loading ? "Checking..." : "Get Download Link"}</Button>
      </Form>

      <br/>
      </div>
      <div>{loading &&  "checking file ..." }</div>
      <br/>
      <br/>
      <br/>
      {!loading && fshareCheck.result && typeof fshareCheck.result === 'string' && fshareCheck.result.startsWith("https") && <Button disabled={loading}  style={{ width: "400px"}} variant="outline-success" onClick={() => window.location = fshareCheck.result }>
        File is Ready. Click Here to Download
      </Button>}
      <br/><br/>
      {!loading &&fshareCheck.result && typeof fshareCheck.result === 'object' && <div>{JSON.stringify(fshareCheck.result) }</div>}
      {!loading && fshareCheck.result && typeof fshareCheck.result === 'string' && <div>{(fshareCheck.result) }</div>}
    </div>
  );
}

export default Ads;
