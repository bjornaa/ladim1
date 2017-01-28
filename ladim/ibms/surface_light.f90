! compile with gfortran -fdec-math

program test

  integer, dimension(6) :: timevec
  real :: lat
  real :: slig

timevec = (/ 2014, 6, 23, 12, 0, 0 /)
lat = 23.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

  
timevec = (/ 2014, 6, 23, 12, 0, 0 /)
lat = 60.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

timevec = (/ 2014, 6, 23, 18, 0, 0 /)
lat = 60.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

timevec = (/ 2014, 6, 23, 18, 0, 0 /)
lat = 80.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

timevec = (/ 2014, 6, 23, 0, 0, 0 /)
lat = 60.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

timevec = (/ 2014, 6, 23, 0, 0, 0 /)
lat = 80.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig



timevec = (/ 2014, 12, 24, 12, 0, 0 /)
lat = 80.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig

timevec = (/ 2014, 12, 24, 12, 0, 0 /)
lat = 60.0
call surf_light(timevec, lat, slig)
print *,  timevec, lat, slig





end program test



!     -------------------------------------------------
      SUBROUTINE surf_light(timevector,B,SLIG)
!     -------------------------------------------------
!   Surface irradiance after Skartveit & Olseth 1988
      implicit none
      integer, dimension(6) :: timevector !y m d h min s
      integer :: i
      integer, dimension(12) :: days_in_month
      REAL     B,D,DELTA,HEIGHT,H,P,V,MAXLIG
      REAL     H12,TWLIGHT
      real :: deg
      real :: SLIG


!     B:Degrees north
!     DELTA: sun declination
!     D: day of the year
!     H: hour of day
!     HEIGHT: sin(sunheight)
!     IRR. irradiance above sea surface uEm-2s-1
!     P: Pi
!     R: factor for distance variations between sun-earth
!     SLIG:surface light
!     V: sunheight in degrees
!     TWLIGHT: light at 0-degree sun
!   MAXLIG: level of irradiance at midday

!FV
      MAXLIG = 1500 ! varierer mellom <200,2000>?!
      D = 0
      days_in_month(1:12) =                                             &
         (/31,28,31,30,31,30,31,31,30,31,30,31/)
      do i = 1,timevector(2)
      D = D + days_in_month(i)
      end do
      D = D - days_in_month(timevector(2)) + timevector(3)
      H = timevector(4)
!FV


      P = 3.1415927
      deg = 180.0 / P
      TWLIGHT = 5.76
        DELTA = .3979*SIN((.9856*(D-80)+ 1.9171*(SIN(.9856*D/deg)-.98112))/deg)
        H12 = DELTA*SIN(B/deg)- SQRT(1.-DELTA**2)*COS(B/deg)*COS(15.*12/deg)
        HEIGHT = DELTA*SIN(B/deg)- SQRT(1.-DELTA**2)*COS(B/deg)*COS(15.*H/deg)

        V = deg * ASIN(HEIGHT)

          IF (V .GE. 0.) THEN
            SLIG = MAXLIG*(HEIGHT/H12) + TWLIGHT
          ELSE IF (V .GE. -6.) THEN
            SLIG = ((TWLIGHT - .048)/6.)*(6.+V)+.048
          ELSE IF (V .GE. -12.) THEN
            SLIG = ((.048 - 1.15E-4)/6.)*(12.+V)+1.15E-4
          ELSE IF (V .GE. -18) THEN
            SLIG = (((1.15E-4)-1.15E-5)/6.)*(18.+V)+1.15E-5
          ELSE
            SLIG = 1.15E-5
          ENDIF


  end subroutine surf_light
