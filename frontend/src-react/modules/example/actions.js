export const addUserToFavourites = user => ({
    type: 'GITHUB_USER_ADD_FAVOURITE',
    payload: { user },
});

export const removeUserFromFavourites = user => ({
    type: 'GITHUB_USER_REMOVE_FAVOURITE',
    payload: { user },
});
