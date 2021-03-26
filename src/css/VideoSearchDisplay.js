import React from "react";
import avatar3 from './avatar3.jpg'
import {Link} from 'react-router-dom'

import {
  MDBRow,
  MDBCol,
  MDBIcon,
  MDBCard,
  MDBCardTitle,
  MDBCardBody,
  MDBCardText,
  MDBContainer,
  MDBCardImage,
  MDBBtn,
  MDBAvatar,
  MDBCardUp,
  MDBView,
  MDBMask,
  MDBListGroup,
  MDBListGroupItem,
  MDBBadge,
} from 'mdbreact';

const DEFAULT_PLACEHOLDER_IMAGE = avatar3

const VideoSearchDisplay = ({video, authType}) => {

	const videoPoster = video.video_thumbnail_url ? video.video_thumbnail_url.S : DEFAULT_PLACEHOLDER_IMAGE
  const ColorCode = 'rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')';
  
  let urlPath = ''
  {video.course_data ?
    authType == "Public" ?
      urlPath =  {pathname:`/public/${video.course_data.M.owner_data.M.given_name.S}/${video.course_data.M.owner_data.M.family_name.S}/${video.course_data.M.owner_data.M.created.N}/courses/${video.course_data.M.course_title.S.replace(/\s/g,'_')}/${video.course_data.M.partition_k.S.replace(/\s/g,'')}/course`, 
                      courseid: video.course_data.M.partition_k.S, 
                      state:{partition_k:video.course_data.M.partition_k.S, sort_k: video.course_data.M.sort_k.S}}
    :
      urlPath =  {pathname:`/${video.course_data.M.owner_data.M.given_name.S}/${video.course_data.M.owner_data.M.family_name.S}/${video.course_data.M.owner_data.M.created.N}/courses/${video.course_data.M.course_title.S.replace(/\s/g,'_')}/course`, 
                      courseid: video.course_data.M.partition_k.S, 
                      state:{partition_k:video.course_data.M.partition_k.S, sort_k: video.course_data.M.sort_k.S}}
  :
    urlPath = ""
  }

  return (
    <MDBCol md='4' className='mb-4'>
      <section>
        <MDBCard>
          <MDBView waves cascade hover>
            <img
              src={video.video_thumbnail_url ? video.video_thumbnail_url.S : 'https://s3-ap-southeast-1.amazonaws.com/itpacs2019/profileimages/Course' + `${Math.floor(Math.random()*(25-1+1))+1}` + '.png'}
              className='img-fluid'
              alt={`video.video_title.S`}
            />
            <MDBMask overlay='white-slight' tag='a' />
          </MDBView>
          <MDBCardBody className='text-center' cascade>
            <MDBCardTitle tag='h4'>
              <br/>
              <strong>
                {video.course_data ?
                  <Link 
                      to={urlPath} 
                  >
                    {video.video_title.S}
                  </Link>
                :
                  <Link to='' className="collapsible-header">
                    {video.video_title.S}
                  </Link>
                }
              </strong>
            </MDBCardTitle>
            <MDBListGroup className='z-depth-1'>
              <MDBListGroupItem className='d-flex justify-content-between align-items-center'>
                Course Title: 
                <div>
                  {video.course_data ? video.course_data.M.course_title.S : ""}
                </div>
              </MDBListGroupItem>
              <MDBListGroupItem className='d-flex justify-content-between align-items-center'>
                Course Creator: 
                <div>
                  {video.course_data?video.course_data.M.owner_data.M.given_name.S:""} {video.course_data?video.course_data.M.owner_data.M.family_name.S:""}
                </div>
              </MDBListGroupItem>
              <MDBListGroupItem className='d-flex justify-content-between align-items-center'>
                Number Of Views:
                <MDBBadge pill color='primary'>
                  30
                </MDBBadge>
              </MDBListGroupItem>
            </MDBListGroup>
            <br/>
          </MDBCardBody>
        </MDBCard>
      </section>
    </MDBCol>
  )
}

export default VideoSearchDisplay
