import api from './api';

// Action types
const types = {
  FETCH_REQUESTED: 'rest_check/FETCH_REQUESTED',
  FETCH_SUCCESS: 'rest_check/FETCH_SUCCESS',
  FETCH_ERROR: 'rest_check/FETCH_ERROR',
};

// Action creators
export const creators = {
  fetchRestCheck: (file_slug) => {
    return async (dispatch) => {
      dispatch({ type: types.FETCH_REQUESTED });
      try {
        const body = { file_slug: file_slug};
        // console.log("fetchRestCheck", body)
        const res = await api.post('/api/rest/run-task/', body);
        // console.log("fetchRestCheck", res.data)
        if(res.status == 200){
          dispatch({ type: types.FETCH_SUCCESS, data: res.data });
        }else{
          dispatch({ type: types.FETCH_ERROR, data: res.data });
        }

      } catch (error) {
        // console.log( error.response.data)
        dispatch({ type: types.FETCH_ERROR, data: error.response.data });
      }
    };
  },
  getFshareLink: (code, server =1, password, token) => {
    return async (dispatch) => {
      dispatch({ type: types.FETCH_REQUESTED });
      try {
        const body = { code: code, server: 2, password: password, token: token};
        console.log("getFshareLink", body)
        var url = server == 1 ? '/api/auth/download_direct/' : '/api/auth/rest_check/'
        const res = await api.post(url , body);
        console.log("getFshareLink", res.data)
        if(res.status == 200){
          dispatch({ type: types.FETCH_SUCCESS, data: res.data });
        }else{
          dispatch({ type: types.FETCH_ERROR, data: res.data });
        }

      } catch (error) {
        // console.log( error.response.data)
        dispatch({ type: types.FETCH_ERROR, data: error.response.data });
      }
    };
  },
};

// Reducer
export const restCheckReducer = (state = {}, action) => {
  // console.log(action.data)
  if (action.type === types.FETCH_SUCCESS) return action.data;
  if (action.type === types.FETCH_ERROR) return action.data;
  return state;
};


// Reducer
export const fshareReducer = (state = {}, action) => {
  // console.log(action.data)
  if (action.type === types.FETCH_SUCCESS) return action.data;
  if (action.type === types.FETCH_ERROR) return action.data;
  return state;
};
