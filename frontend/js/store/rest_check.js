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
        const res = await api.post('/api/rest/run-task/', body);
        dispatch({ type: types.FETCH_SUCCESS, data: res.data });
      } catch (error) {
        dispatch({ type: types.FETCH_ERROR, error });
      }
    };
  },
};

// Reducer
export const restCheckReducer = (state = {}, action) => {
  if (action.type === types.FETCH_SUCCESS) return action.data;
  return state;
};
